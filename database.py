"""
Database module for LegalLex MVP2
Handles all database operations for search results and publications
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class DatabaseManager:
    def __init__(self, db_path: str = "data/legallexmvp2.db"):
        self.db_path = db_path
        # Ensure data directory exists
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            logging.info(f"Database path: {os.path.abspath(db_path)}")
        except Exception as e:
            logging.error(f"Error creating database directory: {str(e)}")
            # Fallback to current directory
            self.db_path = "legallexmvp2.db"
            logging.info(f"Using fallback database path: {os.path.abspath(self.db_path)}")
        self.init_database()
    
    def get_connection(self):
        """Get database connection with foreign key support"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        try:
            # Search executions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    timestamp DATETIME NOT NULL,
                    rules_executed INTEGER,
                    publications_found INTEGER,
                    stats TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, date)
                )
            """)
            
            # Publications table with all API fields
            conn.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_execution_id INTEGER,
                    api_id INTEGER,
                    data_disponibilizacao VARCHAR(50),
                    sigla_tribunal VARCHAR(20),
                    tipo_comunicacao VARCHAR(100),
                    nome_orgao VARCHAR(200),
                    texto TEXT,
                    numero_processo VARCHAR(50),
                    numeroprocessocommascara VARCHAR(50),
                    meio VARCHAR(100),
                    link VARCHAR(500),
                    tipo_documento VARCHAR(100),
                    nome_classe VARCHAR(100),
                    codigo_classe VARCHAR(20),
                    numero_comunicacao INTEGER,
                    ativo BOOLEAN,
                    hash VARCHAR(100),
                    datadisponibilizacao VARCHAR(50),
                    meio_completo VARCHAR(200),
                    source_rule VARCHAR(100),
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (search_execution_id) REFERENCES search_executions(id) ON DELETE CASCADE,
                    UNIQUE(hash, search_execution_id)
                )
            """)
            
            # Destinatarios table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS destinatarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_id INTEGER,
                    nome VARCHAR(200),
                    polo VARCHAR(100),
                    comunicacao_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (publication_id) REFERENCES publications(id) ON DELETE CASCADE
                )
            """)
            
            # Advogados table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS advogados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advogado_id INTEGER,
                    nome VARCHAR(200),
                    numero_oab VARCHAR(20),
                    uf_oab VARCHAR(2),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(advogado_id)
                )
            """)
            
            # Publication-Advogados relationship table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS publication_advogados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_id INTEGER,
                    advogado_id INTEGER,
                    comunicacao_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (publication_id) REFERENCES publications(id) ON DELETE CASCADE,
                    FOREIGN KEY (advogado_id) REFERENCES advogados(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_executions_date ON search_executions(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_publications_hash ON publications(hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_publications_search_exec ON publications(search_execution_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_publications_date ON publications(datadisponibilizacao)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_destinatarios_pub ON destinatarios(publication_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_advogados_oab ON advogados(numero_oab, uf_oab)")
            
            conn.commit()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def save_search_execution(self, name: str, date: str, timestamp: datetime, 
                            rules_executed: int, publications: List[Dict], stats: Dict) -> int:
        """Save a complete search execution with all publications"""
        conn = self.get_connection()
        try:
            # Insert or update search execution
            cursor = conn.execute("""
                INSERT OR REPLACE INTO search_executions 
                (name, date, timestamp, rules_executed, publications_found, stats)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, date, timestamp.isoformat(), rules_executed, len(publications), json.dumps(stats)))
            
            search_execution_id = cursor.lastrowid
            
            # Delete existing publications for this search execution
            conn.execute("DELETE FROM publications WHERE search_execution_id = ?", (search_execution_id,))
            
            # Insert all publications
            for pub in publications:
                pub_id = self._insert_publication(conn, search_execution_id, pub)
                self._insert_destinatarios(conn, pub_id, pub.get('destinatarios', []))
                self._insert_advogados(conn, pub_id, pub.get('destinatarioadvogados', []))
            
            conn.commit()
            logging.info(f"Saved search execution '{name}' with {len(publications)} publications")
            return search_execution_id
            
        except Exception as e:
            logging.error(f"Error saving search execution: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _insert_publication(self, conn: sqlite3.Connection, search_execution_id: int, pub: Dict) -> int:
        """Insert a single publication"""
        cursor = conn.execute("""
            INSERT INTO publications (
                search_execution_id, api_id, data_disponibilizacao, sigla_tribunal,
                tipo_comunicacao, nome_orgao, texto, numero_processo, numeroprocessocommascara,
                meio, link, tipo_documento, nome_classe, codigo_classe, numero_comunicacao,
                ativo, hash, datadisponibilizacao, meio_completo, source_rule, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            search_execution_id,
            pub.get('id'),
            pub.get('data_disponibilizacao'),
            pub.get('siglaTribunal'),
            pub.get('tipoComunicacao'),
            pub.get('nomeOrgao'),
            pub.get('texto'),
            pub.get('numero_processo'),
            pub.get('numeroprocessocommascara'),
            pub.get('meio'),
            pub.get('link'),
            pub.get('tipoDocumento'),
            pub.get('nomeClasse'),
            pub.get('codigoClasse'),
            pub.get('numeroComunicacao'),
            pub.get('ativo'),
            pub.get('hash'),
            pub.get('datadisponibilizacao'),
            pub.get('meiocompleto'),
            pub.get('_source_rule'),
            json.dumps(pub)  # Store full JSON as backup
        ))
        return cursor.lastrowid
    
    def _insert_destinatarios(self, conn: sqlite3.Connection, publication_id: int, destinatarios: List[Dict]):
        """Insert destinatarios for a publication"""
        for dest in destinatarios:
            conn.execute("""
                INSERT INTO destinatarios (publication_id, nome, polo, comunicacao_id)
                VALUES (?, ?, ?, ?)
            """, (publication_id, dest.get('nome'), dest.get('polo'), dest.get('comunicacao_id')))
    
    def _insert_advogados(self, conn: sqlite3.Connection, publication_id: int, advogados_data: List[Dict]):
        """Insert advogados and their relationship to publications"""
        for adv_data in advogados_data:
            advogado_info = adv_data.get('advogado', {})
            advogado_id = advogado_info.get('id')
            
            if advogado_id:
                # Insert or update advogado
                conn.execute("""
                    INSERT OR REPLACE INTO advogados (advogado_id, nome, numero_oab, uf_oab)
                    VALUES (?, ?, ?, ?)
                """, (
                    advogado_id,
                    advogado_info.get('nome'),
                    advogado_info.get('numero_oab'),
                    advogado_info.get('uf_oab')
                ))
                
                # Insert publication-advogado relationship
                conn.execute("""
                    INSERT INTO publication_advogados (publication_id, advogado_id, comunicacao_id)
                    VALUES (?, ?, ?)
                """, (publication_id, advogado_id, adv_data.get('comunicacao_id')))
    
    def get_search_execution_by_date(self, date: str) -> Optional[Dict]:
        """Get search execution by date"""
        conn = self.get_connection()
        try:
            cursor = conn.execute("""
                SELECT * FROM search_executions WHERE date = ? ORDER BY timestamp DESC LIMIT 1
            """, (date,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            logging.error(f"Error getting search execution by date: {str(e)}")
            return None
        finally:
            conn.close()
    
    def get_publications_by_search_execution(self, search_execution_id: int) -> List[Dict]:
        """Get all publications for a search execution with destinatarios and advogados"""
        conn = self.get_connection()
        try:
            # Get publications
            cursor = conn.execute("""
                SELECT * FROM publications WHERE search_execution_id = ?
            """, (search_execution_id,))
            
            publications = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                pub = dict(zip(columns, row))
                
                # Get destinatarios
                dest_cursor = conn.execute("""
                    SELECT nome, polo, comunicacao_id FROM destinatarios WHERE publication_id = ?
                """, (pub['id'],))
                pub['destinatarios'] = [
                    {'nome': row[0], 'polo': row[1], 'comunicacao_id': row[2]}
                    for row in dest_cursor.fetchall()
                ]
                
                # Get advogados
                adv_cursor = conn.execute("""
                    SELECT a.advogado_id, a.nome, a.numero_oab, a.uf_oab, pa.comunicacao_id
                    FROM advogados a
                    JOIN publication_advogados pa ON a.advogado_id = pa.advogado_id
                    WHERE pa.publication_id = ?
                """, (pub['id'],))
                pub['destinatarioadvogados'] = [
                    {
                        'comunicacao_id': row[4],
                        'advogado_id': row[0],
                        'advogado': {
                            'id': row[0],
                            'nome': row[1],
                            'numero_oab': row[2],
                            'uf_oab': row[3]
                        }
                    }
                    for row in adv_cursor.fetchall()
                ]
                
                # Map database field names back to API field names for compatibility
                api_pub = {
                    'id': pub['api_id'],
                    'data_disponibilizacao': pub['data_disponibilizacao'],
                    'siglaTribunal': pub['sigla_tribunal'],
                    'tipoComunicacao': pub['tipo_comunicacao'],
                    'nomeOrgao': pub['nome_orgao'],
                    'texto': pub['texto'],
                    'numero_processo': pub['numero_processo'],
                    'numeroprocessocommascara': pub['numeroprocessocommascara'],
                    'meio': pub['meio'],
                    'link': pub['link'],
                    'tipoDocumento': pub['tipo_documento'],
                    'nomeClasse': pub['nome_classe'],
                    'codigoClasse': pub['codigo_classe'],
                    'numeroComunicacao': pub['numero_comunicacao'],
                    'ativo': pub['ativo'],
                    'hash': pub['hash'],
                    'datadisponibilizacao': pub['datadisponibilizacao'],
                    'meiocompleto': pub['meio_completo'],
                    '_source_rule': pub['source_rule'],
                    'destinatarios': pub['destinatarios'],
                    'destinatarioadvogados': pub['destinatarioadvogados']
                }
                
                publications.append(api_pub)
            
            return publications
            
        except Exception as e:
            logging.error(f"Error getting publications by search execution: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_publications_by_date(self, date: str) -> List[Dict]:
        """Get all publications for a specific date"""
        search_execution = self.get_search_execution_by_date(date)
        if search_execution:
            return self.get_publications_by_search_execution(search_execution['id'])
        return []
    
    def get_search_history(self, limit: int = 50) -> List[Dict]:
        """Get search execution history"""
        conn = self.get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, name, date, timestamp, rules_executed, publications_found
                FROM search_executions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Error getting search history: {str(e)}")
            return []
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        try:
            stats = {}
            
            # Total search executions
            cursor = conn.execute("SELECT COUNT(*) FROM search_executions")
            stats['total_searches'] = cursor.fetchone()[0]
            
            # Total publications
            cursor = conn.execute("SELECT COUNT(*) FROM publications")
            stats['total_publications'] = cursor.fetchone()[0]
            
            # Total unique advogados
            cursor = conn.execute("SELECT COUNT(*) FROM advogados")
            stats['total_advogados'] = cursor.fetchone()[0]
            
            # Publications by tribunal
            cursor = conn.execute("""
                SELECT sigla_tribunal, COUNT(*) 
                FROM publications 
                GROUP BY sigla_tribunal 
                ORDER BY COUNT(*) DESC
            """)
            stats['publications_by_tribunal'] = dict(cursor.fetchall())
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {}
        finally:
            conn.close()