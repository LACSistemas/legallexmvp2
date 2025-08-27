import json
import os
import pickle
import schedule
import time
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any
import logging
from publiregras import EnhancedDJESearcher, SearchRule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cronjob.log'),
        logging.StreamHandler()
    ]
)

class CronJobScheduler:
    def __init__(self):
        self.rules_file = "data/saved_rules.json"
        self.results_dir = "daily_results"
        self.brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Ensure directories exist
        os.makedirs("data", exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_saved_rules(self) -> List[SearchRule]:
        """Load saved rules from file"""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                
                rules = []
                for rule_data in rules_data:
                    # Reconstruct SearchRule objects
                    from publiregras import RuleType, RuleOperator
                    rule = SearchRule(
                        name=rule_data['name'],
                        rule_type=RuleType(rule_data['rule_type']),
                        operator=RuleOperator(rule_data['operator']),
                        enabled=rule_data['enabled'],
                        parameters=rule_data['parameters']
                    )
                    rules.append(rule)
                
                return rules
        except Exception as e:
            logging.error(f"Error loading rules: {str(e)}")
        
        return []
    
    def load_all_rules(self) -> List[SearchRule]:
        """Load all rules (default hardcoded + custom saved rules)"""
        from djesearchapp import SearchRule
        
        # Default hardcoded rules that always exist
        from datetime import datetime
        
        default_rules = [
            SearchRule(
                name="OAB Principal",
                enabled=True,
                parameters={
                    'numeroOab': '8773', 
                    'ufOab': 'ES',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Darwin",
                enabled=True,
                parameters={
                    'nomeParte': 'Darwin', 
                    'siglaOrgaoJulgador': 'TJES',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Sinales",
                enabled=True,
                parameters={
                    'nomeParte': 'Sinales',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Multivix",
                enabled=True,
                parameters={
                    'nomeParte': 'Multivix',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            ),
            SearchRule(
                name="Claretiano",
                enabled=True,
                parameters={
                    'nomeParte': 'Claretiano',
                    'dataDisponibilizacaoInicio': datetime.now().strftime('%Y-%m-%d')
                }
            )
        ]
        
        # Load additional custom rules from file
        custom_rules = self.load_saved_rules()
        
        # Combine default + custom rules
        all_rules = default_rules + custom_rules
        logging.info(f"Loaded {len(default_rules)} default rules + {len(custom_rules)} custom rules")
        
        return all_rules
    
    def save_rules(self, rules: List[SearchRule]):
        """Save rules to file"""
        try:
            rules_data = []
            for rule in rules:
                rule_data = {
                    'name': rule.name,
                    'rule_type': rule.rule_type.value,
                    'operator': rule.operator.value,
                    'enabled': rule.enabled,
                    'parameters': rule.parameters
                }
                rules_data.append(rule_data)
            
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Saved {len(rules)} rules to {self.rules_file}")
        except Exception as e:
            logging.error(f"Error saving rules: {str(e)}")
    
    def execute_daily_search(self):
        """Execute the daily automated search"""
        brasilia_now = datetime.now(self.brasilia_tz)
        logging.info(f"Starting daily search at {brasilia_now.strftime('%Y-%m-%d %H:%M:%S')} (Brasília)")
        
        # Load all rules (default + custom)
        rules = self.load_all_rules()
        if not rules:
            logging.warning("No rules configured for daily search")
            return
        
        # Filter enabled rules
        enabled_rules = [rule for rule in rules if rule.enabled]
        if not enabled_rules:
            logging.warning("No enabled rules found for daily search")
            return
        
        logging.info(f"Executing search with {len(enabled_rules)} enabled rules")
        
        try:
            # Execute search
            searcher = EnhancedDJESearcher()
            
            def log_progress(message):
                logging.info(f"Search progress: {message}")
            
            publications = searcher.execute_rules(enabled_rules, log_progress)
            
            # Save results
            date_str = brasilia_now.strftime('%Y-%m-%d')
            results_file = os.path.join(self.results_dir, f"results_{date_str}.json")
            
            results_data = {
                'date': date_str,
                'timestamp': brasilia_now.isoformat(),
                'rules_executed': len(enabled_rules),
                'publications_found': len(publications),
                'publications': publications
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Daily search completed successfully. Found {len(publications)} publications. Results saved to {results_file}")
            
        except Exception as e:
            logging.error(f"Error during daily search: {str(e)}")
    
    def get_daily_results(self, date_str: str) -> Dict[str, Any]:
        """Get results for a specific date"""
        results_file = os.path.join(self.results_dir, f"results_{date_str}.json")
        
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading results for {date_str}: {str(e)}")
        
        return None
    
    def schedule_daily_job(self):
        """Schedule the daily job for 6:00 AM Brasília time"""
        # Schedule for 6:00 AM every day
        schedule.every().day.at("06:00").do(self.execute_daily_search)
        logging.info("Daily job scheduled for 6:00 AM Brasília time")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.schedule_daily_job()
        logging.info("Cronjob scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("Cronjob scheduler stopped by user")

def main():
    scheduler = CronJobScheduler()
    
    # For testing, you can run a manual search
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "test":
        logging.info("Running test search...")
        scheduler.execute_daily_search()
    else:
        # Run the scheduler
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()