"""
V5.0 Query Translator - Cross-Database Compatibility
Translates queries between different database dialects for unified interface
"""

import re
import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from database_adapters import DatabaseType

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of SQL queries"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE_TABLE = "create_table"
    ALTER_TABLE = "alter_table"
    DROP_TABLE = "drop_table"
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    TRANSACTION = "transaction"
    UNKNOWN = "unknown"


class TranslationError(Exception):
    """Raised when query translation fails"""
    pass


@dataclass
class QueryTranslationResult:
    """Result of query translation"""
    success: bool
    translated_query: Optional[str] = None
    translated_parameters: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None
    translation_notes: Optional[List[str]] = None
    original_query: Optional[str] = None
    target_database: Optional[DatabaseType] = None
    query_type: Optional[QueryType] = None
    translation_time: float = 0.0


@dataclass
class DatabaseDialectFeatures:
    """Database-specific feature support"""
    supports_window_functions: bool = True
    supports_cte: bool = True  # Common Table Expressions
    supports_json: bool = True
    supports_arrays: bool = False
    supports_regex: bool = True
    supports_full_text_search: bool = True
    auto_increment_syntax: str = "AUTO_INCREMENT"
    limit_syntax: str = "LIMIT"
    quote_identifier: str = "`"
    string_concatenation: str = "CONCAT"
    date_format_function: str = "DATE_FORMAT"
    current_timestamp: str = "CURRENT_TIMESTAMP"
    boolean_true: str = "TRUE"
    boolean_false: str = "FALSE"


class QueryTranslator(ABC):
    """Abstract base class for database query translators"""
    
    def __init__(self, target_database: DatabaseType):
        self.target_database = target_database
        self.features = self._get_dialect_features()
        self.translation_cache: Dict[str, QueryTranslationResult] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
    @abstractmethod
    def _get_dialect_features(self) -> DatabaseDialectFeatures:
        """Get database-specific dialect features"""
        pass
    
    @abstractmethod
    def translate_data_types(self, data_type: str) -> str:
        """Translate data types between databases"""
        pass
    
    @abstractmethod
    def translate_functions(self, function_call: str) -> str:
        """Translate function calls between databases"""
        pass
    
    @abstractmethod
    def translate_operators(self, operator: str) -> str:
        """Translate operators between databases"""
        pass
    
    def translate_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        source_database: Optional[DatabaseType] = None
    ) -> QueryTranslationResult:
        """Main query translation method"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{query}_{parameters}_{source_database}"
        if cache_key in self.translation_cache:
            self.cache_hits += 1
            cached_result = self.translation_cache[cache_key]
            cached_result.translation_time = time.time() - start_time
            return cached_result
        
        self.cache_misses += 1
        
        try:
            # Determine query type
            query_type = self._detect_query_type(query)
            
            # Normalize query
            normalized_query = self._normalize_query(query)
            
            # Translate based on query type
            translated_query = self._translate_by_type(normalized_query, query_type, source_database)
            
            # Translate parameters if needed
            translated_params = self._translate_parameters(parameters, source_database)
            
            # Validate translation
            warnings = self._validate_translation(translated_query, query_type)
            
            translation_time = time.time() - start_time
            
            result = QueryTranslationResult(
                success=True,
                translated_query=translated_query,
                translated_parameters=translated_params,
                warnings=warnings,
                original_query=query,
                target_database=self.target_database,
                query_type=query_type,
                translation_time=translation_time
            )
            
            # Cache result
            self.translation_cache[cache_key] = result
            
            logger.debug(f"Query translated successfully to {self.target_database.value}")
            return result
            
        except Exception as e:
            translation_time = time.time() - start_time
            
            logger.error(f"Query translation failed: {e}")
            return QueryTranslationResult(
                success=False,
                original_query=query,
                target_database=self.target_database,
                translation_time=translation_time,
                warnings=[f"Translation failed: {str(e)}"]
            )
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detect the type of SQL query"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE TABLE'):
            return QueryType.CREATE_TABLE
        elif query_upper.startswith('ALTER TABLE'):
            return QueryType.ALTER_TABLE
        elif query_upper.startswith('DROP TABLE'):
            return QueryType.DROP_TABLE
        elif query_upper.startswith('CREATE INDEX'):
            return QueryType.CREATE_INDEX
        elif query_upper.startswith('DROP INDEX'):
            return QueryType.DROP_INDEX
        elif any(query_upper.startswith(cmd) for cmd in ['BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT']):
            return QueryType.TRANSACTION
        else:
            return QueryType.UNKNOWN
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query formatting"""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', query.strip())
        return normalized
    
    def _translate_by_type(
        self, 
        query: str, 
        query_type: QueryType, 
        source_database: Optional[DatabaseType]
    ) -> str:
        """Translate query based on its type"""
        
        if query_type == QueryType.SELECT:
            return self._translate_select_query(query, source_database)
        elif query_type == QueryType.INSERT:
            return self._translate_insert_query(query, source_database)
        elif query_type == QueryType.UPDATE:
            return self._translate_update_query(query, source_database)
        elif query_type == QueryType.DELETE:
            return self._translate_delete_query(query, source_database)
        elif query_type == QueryType.CREATE_TABLE:
            return self._translate_create_table_query(query, source_database)
        elif query_type == QueryType.ALTER_TABLE:
            return self._translate_alter_table_query(query, source_database)
        elif query_type == QueryType.TRANSACTION:
            return self._translate_transaction_query(query, source_database)
        else:
            return query  # Return as-is for unknown types
    
    def _translate_select_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate SELECT queries"""
        translated = query
        
        # Translate LIMIT syntax (check for SQL Server that we don't support)
        if hasattr(DatabaseType, 'SQLSERVER') and self.target_database == DatabaseType.SQLSERVER:
            # SQL Server uses TOP instead of LIMIT
            limit_pattern = r'LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?'
            match = re.search(limit_pattern, translated, re.IGNORECASE)
            if match:
                limit_count = match.group(1)
                offset_count = match.group(2) if match.group(2) else '0'
                
                if offset_count == '0':
                    replacement = f'TOP {limit_count}'
                    translated = re.sub(r'SELECT\s+', f'SELECT {replacement} ', translated, flags=re.IGNORECASE)
                    translated = re.sub(limit_pattern, '', translated, flags=re.IGNORECASE)
                else:
                    # SQL Server 2012+ OFFSET/FETCH syntax
                    replacement = f'OFFSET {offset_count} ROWS FETCH NEXT {limit_count} ROWS ONLY'
                    translated = re.sub(limit_pattern, replacement, translated, flags=re.IGNORECASE)
        
        # Translate functions
        translated = self._translate_function_calls(translated)
        
        # Translate data types in CAST operations
        translated = self._translate_cast_operations(translated)
        
        return translated
    
    def _translate_insert_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate INSERT queries"""
        translated = query
        
        # Translate ON DUPLICATE KEY UPDATE (MySQL) to UPSERT equivalents
        if 'ON DUPLICATE KEY UPDATE' in translated.upper():
            if self.target_database == DatabaseType.POSTGRESQL:
                # Convert to ON CONFLICT ... DO UPDATE
                translated = self._convert_mysql_upsert_to_postgresql(translated)
            elif self.target_database == DatabaseType.SQLITE:
                # Convert to INSERT OR REPLACE
                translated = self._convert_mysql_upsert_to_sqlite(translated)
        
        return translated
    
    def _translate_update_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate UPDATE queries"""
        return query  # Most UPDATE syntax is standard
    
    def _translate_delete_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate DELETE queries"""
        return query  # Most DELETE syntax is standard
    
    def _translate_create_table_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate CREATE TABLE queries"""
        translated = query
        
        # Translate data types
        translated = self._translate_data_type_definitions(translated)
        
        # Translate auto-increment syntax
        if 'AUTO_INCREMENT' in translated.upper():
            if self.target_database == DatabaseType.POSTGRESQL:
                translated = re.sub(r'AUTO_INCREMENT', 'SERIAL', translated, flags=re.IGNORECASE)
            elif self.target_database == DatabaseType.SQLITE:
                translated = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', translated, flags=re.IGNORECASE)
        
        return translated
    
    def _translate_alter_table_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate ALTER TABLE queries"""
        return self._translate_data_type_definitions(query)
    
    def _translate_transaction_query(self, query: str, source_database: Optional[DatabaseType]) -> str:
        """Translate transaction control queries"""
        # Most transaction syntax is standard across databases
        return query
    
    def _translate_function_calls(self, query: str) -> str:
        """Translate function calls in query"""
        translated = query
        
        # String concatenation
        if self.target_database == DatabaseType.POSTGRESQL:
            # PostgreSQL uses || for concatenation
            translated = re.sub(r'CONCAT\s*\(([^)]+)\)', r'(\1)', translated, flags=re.IGNORECASE)
            translated = re.sub(r'\s*\+\s*', ' || ', translated)
        elif self.target_database == DatabaseType.SQLITE:
            # SQLite uses || for concatenation
            translated = re.sub(r'CONCAT\s*\(([^)]+)\)', r'(\1)', translated, flags=re.IGNORECASE)
            translated = re.sub(r'\s*\+\s*', ' || ', translated)
        
        # Date functions
        if self.target_database == DatabaseType.POSTGRESQL:
            translated = re.sub(r'NOW\(\)', 'CURRENT_TIMESTAMP', translated, flags=re.IGNORECASE)
        elif self.target_database == DatabaseType.SQLITE:
            translated = re.sub(r'NOW\(\)', "datetime('now')", translated, flags=re.IGNORECASE)
        
        return translated
    
    def _translate_cast_operations(self, query: str) -> str:
        """Translate CAST operations between databases"""
        # Find all CAST operations
        cast_pattern = r'CAST\s*\(\s*([^)]+)\s+AS\s+([^)]+)\s*\)'
        
        def replace_cast(match):
            expression = match.group(1).strip()
            data_type = match.group(2).strip()
            translated_type = self.translate_data_types(data_type)
            return f'CAST({expression} AS {translated_type})'
        
        return re.sub(cast_pattern, replace_cast, query, flags=re.IGNORECASE)
    
    def _translate_data_type_definitions(self, query: str) -> str:
        """Translate data type definitions in DDL"""
        translated = query
        
        # Common data type mappings
        type_mappings = {
            r'\bTINYINT\b': self.translate_data_types('TINYINT'),
            r'\bSMALLINT\b': self.translate_data_types('SMALLINT'),
            r'\bMEDIUMINT\b': self.translate_data_types('MEDIUMINT'),
            r'\bBIGINT\b': self.translate_data_types('BIGINT'),
            r'\bTEXT\b': self.translate_data_types('TEXT'),
            r'\bBLOB\b': self.translate_data_types('BLOB'),
            r'\bDATETIME\b': self.translate_data_types('DATETIME'),
            r'\bTIMESTAMP\b': self.translate_data_types('TIMESTAMP')
        }
        
        for pattern, replacement in type_mappings.items():
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        
        return translated
    
    def _convert_mysql_upsert_to_postgresql(self, query: str) -> str:
        """Convert MySQL ON DUPLICATE KEY UPDATE to PostgreSQL ON CONFLICT"""
        # This is a simplified conversion - real implementation would be more complex
        pattern = r'ON DUPLICATE KEY UPDATE\s+(.+)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if match:
            update_clause = match.group(1)
            # Remove the ON DUPLICATE KEY UPDATE clause
            base_query = re.sub(pattern, '', query, flags=re.IGNORECASE)
            # Add PostgreSQL ON CONFLICT clause (simplified)
            return f"{base_query} ON CONFLICT DO UPDATE SET {update_clause}"
        
        return query
    
    def _convert_mysql_upsert_to_sqlite(self, query: str) -> str:
        """Convert MySQL ON DUPLICATE KEY UPDATE to SQLite INSERT OR REPLACE"""
        # Simplified conversion
        if 'ON DUPLICATE KEY UPDATE' in query.upper():
            return re.sub(r'INSERT\s+INTO', 'INSERT OR REPLACE INTO', query, flags=re.IGNORECASE)
        return query
    
    def _translate_parameters(
        self, 
        parameters: Optional[Dict[str, Any]], 
        source_database: Optional[DatabaseType]
    ) -> Optional[Dict[str, Any]]:
        """Translate parameter values if needed"""
        if not parameters:
            return parameters
        
        # Most parameter translation is handled by drivers
        return parameters
    
    def _validate_translation(self, query: str, query_type: QueryType) -> List[str]:
        """Validate translated query and return warnings"""
        warnings = []
        
        # Check for unsupported features
        if not self.features.supports_cte and 'WITH ' in query.upper():
            warnings.append("Common Table Expressions (CTE) may not be supported")
        
        if not self.features.supports_window_functions and 'OVER(' in query.upper():
            warnings.append("Window functions may not be supported")
        
        if not self.features.supports_json and any(func in query.upper() for func in ['JSON_', 'JSON(']):
            warnings.append("JSON functions may not be supported")
        
        return warnings
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / max(total_requests, 1)
        
        return {
            "total_translations": total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "cached_queries": len(self.translation_cache),
            "target_database": self.target_database.value
        }


class PostgreSQLTranslator(QueryTranslator):
    """Query translator for PostgreSQL database"""
    
    def _get_dialect_features(self) -> DatabaseDialectFeatures:
        return DatabaseDialectFeatures(
            supports_window_functions=True,
            supports_cte=True,
            supports_json=True,
            supports_arrays=True,
            supports_regex=True,
            supports_full_text_search=True,
            auto_increment_syntax="SERIAL",
            limit_syntax="LIMIT",
            quote_identifier='"',
            string_concatenation="||",
            date_format_function="TO_CHAR",
            current_timestamp="CURRENT_TIMESTAMP",
            boolean_true="TRUE",
            boolean_false="FALSE"
        )
    
    def translate_data_types(self, data_type: str) -> str:
        """Translate data types to PostgreSQL"""
        type_map = {
            'TINYINT': 'SMALLINT',
            'MEDIUMINT': 'INTEGER',
            'LONGTEXT': 'TEXT',
            'MEDIUMTEXT': 'TEXT',
            'TINYTEXT': 'TEXT',
            'BLOB': 'BYTEA',
            'LONGBLOB': 'BYTEA',
            'MEDIUMBLOB': 'BYTEA',
            'TINYBLOB': 'BYTEA',
            'DATETIME': 'TIMESTAMP',
            'AUTO_INCREMENT': 'SERIAL'
        }
        
        return type_map.get(data_type.upper(), data_type)
    
    def translate_functions(self, function_call: str) -> str:
        """Translate functions to PostgreSQL"""
        # PostgreSQL-specific function translations
        translations = {
            'CONCAT': '||',
            'IFNULL': 'COALESCE',
            'NOW()': 'CURRENT_TIMESTAMP',
            'CURDATE()': 'CURRENT_DATE',
            'CURTIME()': 'CURRENT_TIME'
        }
        
        for mysql_func, pg_func in translations.items():
            function_call = re.sub(mysql_func, pg_func, function_call, flags=re.IGNORECASE)
        
        return function_call
    
    def translate_operators(self, operator: str) -> str:
        """Translate operators to PostgreSQL"""
        operator_map = {
            'REGEXP': '~',
            'NOT REGEXP': '!~',
            'RLIKE': '~'
        }
        
        return operator_map.get(operator.upper(), operator)


class MySQLTranslator(QueryTranslator):
    """Query translator for MySQL database"""
    
    def _get_dialect_features(self) -> DatabaseDialectFeatures:
        return DatabaseDialectFeatures(
            supports_window_functions=True,  # MySQL 8.0+
            supports_cte=True,  # MySQL 8.0+
            supports_json=True,  # MySQL 5.7+
            supports_arrays=False,
            supports_regex=True,
            supports_full_text_search=True,
            auto_increment_syntax="AUTO_INCREMENT",
            limit_syntax="LIMIT",
            quote_identifier="`",
            string_concatenation="CONCAT",
            date_format_function="DATE_FORMAT",
            current_timestamp="CURRENT_TIMESTAMP",
            boolean_true="TRUE",
            boolean_false="FALSE"
        )
    
    def translate_data_types(self, data_type: str) -> str:
        """Translate data types to MySQL"""
        type_map = {
            'SERIAL': 'INT AUTO_INCREMENT',
            'BYTEA': 'BLOB',
            'BOOLEAN': 'TINYINT(1)',
            'TEXT': 'LONGTEXT'
        }
        
        return type_map.get(data_type.upper(), data_type)
    
    def translate_functions(self, function_call: str) -> str:
        """Translate functions to MySQL"""
        # MySQL-specific function translations
        translations = {
            'COALESCE': 'IFNULL',
            'CURRENT_TIMESTAMP': 'NOW()',
            'CURRENT_DATE': 'CURDATE()',
            'CURRENT_TIME': 'CURTIME()'
        }
        
        for standard_func, mysql_func in translations.items():
            function_call = re.sub(standard_func, mysql_func, function_call, flags=re.IGNORECASE)
        
        return function_call
    
    def translate_operators(self, operator: str) -> str:
        """Translate operators to MySQL"""
        operator_map = {
            '~': 'REGEXP',
            '!~': 'NOT REGEXP'
        }
        
        return operator_map.get(operator, operator)


class SQLiteTranslator(QueryTranslator):
    """Query translator for SQLite database"""
    
    def _get_dialect_features(self) -> DatabaseDialectFeatures:
        return DatabaseDialectFeatures(
            supports_window_functions=True,  # SQLite 3.25+
            supports_cte=True,
            supports_json=True,  # SQLite 3.38+
            supports_arrays=False,
            supports_regex=False,  # Limited support
            supports_full_text_search=True,  # With FTS extension
            auto_increment_syntax="AUTOINCREMENT",
            limit_syntax="LIMIT",
            quote_identifier='"',
            string_concatenation="||",
            date_format_function="strftime",
            current_timestamp="datetime('now')",
            boolean_true="1",
            boolean_false="0"
        )
    
    def translate_data_types(self, data_type: str) -> str:
        """Translate data types to SQLite"""
        type_map = {
            'TINYINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'MEDIUMINT': 'INTEGER',
            'BIGINT': 'INTEGER',
            'DECIMAL': 'REAL',
            'FLOAT': 'REAL',
            'DOUBLE': 'REAL',
            'DATETIME': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'BLOB': 'BLOB',
            'BYTEA': 'BLOB',
            'BOOLEAN': 'INTEGER',
            'SERIAL': 'INTEGER PRIMARY KEY AUTOINCREMENT'
        }
        
        return type_map.get(data_type.upper(), data_type)
    
    def translate_functions(self, function_call: str) -> str:
        """Translate functions to SQLite"""
        # SQLite-specific function translations
        translations = {
            'CONCAT': '||',
            'NOW()': "datetime('now')",
            'CURDATE()': "date('now')",
            'CURTIME()': "time('now')",
            'CURRENT_TIMESTAMP': "datetime('now')"
        }
        
        for standard_func, sqlite_func in translations.items():
            function_call = re.sub(standard_func, sqlite_func, function_call, flags=re.IGNORECASE)
        
        return function_call
    
    def translate_operators(self, operator: str) -> str:
        """Translate operators to SQLite"""
        # SQLite has limited regex support
        operator_map = {
            'REGEXP': 'LIKE',  # Fallback to LIKE
            'NOT REGEXP': 'NOT LIKE',
            'RLIKE': 'LIKE'
        }
        
        return operator_map.get(operator.upper(), operator)


class UniversalQueryTranslator:
    """Universal query translator that can translate between any supported databases"""
    
    def __init__(self):
        self.translators = {
            DatabaseType.POSTGRESQL: PostgreSQLTranslator(DatabaseType.POSTGRESQL),
            DatabaseType.MYSQL: MySQLTranslator(DatabaseType.MYSQL),
            DatabaseType.SQLITE: SQLiteTranslator(DatabaseType.SQLITE)
        }
        
        self.translation_statistics = {
            "total_translations": 0,
            "successful_translations": 0,
            "failed_translations": 0,
            "translations_by_target": {db.value: 0 for db in DatabaseType}
        }
    
    def translate(
        self,
        query: str,
        target_database: DatabaseType,
        parameters: Optional[Dict[str, Any]] = None,
        source_database: Optional[DatabaseType] = None
    ) -> QueryTranslationResult:
        """Translate query to target database dialect"""
        
        self.translation_statistics["total_translations"] += 1
        
        try:
            if target_database not in self.translators:
                raise TranslationError(f"Unsupported target database: {target_database}")
            
            translator = self.translators[target_database]
            result = translator.translate_query(query, parameters, source_database)
            
            if result.success:
                self.translation_statistics["successful_translations"] += 1
                self.translation_statistics["translations_by_target"][target_database.value] += 1
            else:
                self.translation_statistics["failed_translations"] += 1
            
            return result
            
        except Exception as e:
            self.translation_statistics["failed_translations"] += 1
            
            return QueryTranslationResult(
                success=False,
                original_query=query,
                target_database=target_database,
                warnings=[f"Translation failed: {str(e)}"]
            )
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global translation statistics"""
        stats = self.translation_statistics.copy()
        
        # Add per-translator statistics
        translator_stats = {}
        for db_type, translator in self.translators.items():
            translator_stats[db_type.value] = translator.get_translation_statistics()
        
        stats["translator_statistics"] = translator_stats
        
        return stats


# Test harness
if __name__ == "__main__":
    async def test_query_translator():
        """Test query translation functionality"""
        
        print("🔧 Testing Query Translator...")
        
        # Create universal translator
        translator = UniversalQueryTranslator()
        
        # Test queries
        test_queries = [
            "SELECT * FROM users WHERE id = %(user_id)s LIMIT 10",
            "INSERT INTO users (name, email) VALUES ('John', 'john@example.com') ON DUPLICATE KEY UPDATE email = VALUES(email)",
            "CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), created_at DATETIME)",
            "SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users",
            "SELECT * FROM orders WHERE created_at >= NOW() - INTERVAL 1 DAY"
        ]
        
        # Test translation to different databases
        for query in test_queries:
            print(f"\n🔄 Testing query: {query[:50]}...")
            
            # Test PostgreSQL translation
            pg_result = translator.translate(query, DatabaseType.POSTGRESQL, {"user_id": 1})
            print(f"  PostgreSQL: {'✅' if pg_result.success else '❌'} {pg_result.translated_query[:60] if pg_result.translated_query else 'Failed'}")
            if pg_result.warnings:
                print(f"    Warnings: {pg_result.warnings}")
            
            # Test MySQL translation
            mysql_result = translator.translate(query, DatabaseType.MYSQL)
            print(f"  MySQL: {'✅' if mysql_result.success else '❌'} {mysql_result.translated_query[:60] if mysql_result.translated_query else 'Failed'}")
            
            # Test SQLite translation
            sqlite_result = translator.translate(query, DatabaseType.SQLITE)
            print(f"  SQLite: {'✅' if sqlite_result.success else '❌'} {sqlite_result.translated_query[:60] if sqlite_result.translated_query else 'Failed'}")
        
        # Test specific translator features
        pg_translator = translator.translators[DatabaseType.POSTGRESQL]
        
        # Test data type translation
        print(f"\n🔧 Data type translations:")
        print(f"  TINYINT -> {pg_translator.translate_data_types('TINYINT')}")
        print(f"  DATETIME -> {pg_translator.translate_data_types('DATETIME')}")
        print(f"  AUTO_INCREMENT -> {pg_translator.translate_data_types('AUTO_INCREMENT')}")
        
        # Test function translation
        print(f"\n🔧 Function translations:")
        print(f"  CONCAT -> {pg_translator.translate_functions('CONCAT(a, b)')}")
        print(f"  NOW() -> {pg_translator.translate_functions('NOW()')}")
        
        # Test statistics
        print(f"\n📊 Translation Statistics:")
        stats = translator.get_global_statistics()
        print(f"  Total translations: {stats['total_translations']}")
        print(f"  Successful: {stats['successful_translations']}")
        print(f"  Failed: {stats['failed_translations']}")
        print(f"  By target database: {stats['translations_by_target']}")
        
        print("\n🎉 Query translator testing complete!")
    
    import asyncio
    asyncio.run(test_query_translator())