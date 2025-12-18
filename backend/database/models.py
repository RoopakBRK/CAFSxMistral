"""
Database models for verification history
"""

import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
import json


class VerificationHistory:
    """SQLite database for verification history"""
    
    def __init__(self, db_path: str = "verification_history.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT,
                student_name TEXT,
                issuer TEXT,
                course_name TEXT,
                certificate_id TEXT,
                is_verified BOOLEAN,
                verification_method TEXT,
                confidence_score REAL,
                is_high_risk BOOLEAN,
                manipulation_score REAL,
                verification_url TEXT,
                raw_data TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_verification(self, data: Dict[str, Any]) -> int:
        """
        Add a verification to history.
        
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract fields
        extracted = data.get('extracted_data', {})
        verification = data.get('verification', {})
        forensics = data.get('forensics', {})
        
        cursor.execute("""
            INSERT INTO verifications (
                timestamp, filename, student_name, issuer, course_name,
                certificate_id, is_verified, verification_method,
                confidence_score, is_high_risk, manipulation_score,
                verification_url, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            data.get('filename'),
            extracted.get('student_name'),
            extracted.get('issuer'),
            extracted.get('course_name'),
            extracted.get('certificate_ids', [None])[0] if extracted.get('certificate_ids') else None,
            verification.get('is_verified'),
            verification.get('method'),
            verification.get('confidence_score'),
            forensics.get('is_high_risk'),
            forensics.get('manipulation_score'),
            verification.get('verification_url'),
            json.dumps(data)  # Store full data as JSON
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent verifications"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM verifications
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total verifications
        cursor.execute("SELECT COUNT(*) FROM verifications")
        total = cursor.fetchone()[0]
        
        # Verified count
        cursor.execute("SELECT COUNT(*) FROM verifications WHERE is_verified = 1")
        verified = cursor.fetchone()[0]
        
        # High risk count
        cursor.execute("SELECT COUNT(*) FROM verifications WHERE is_high_risk = 1")
        high_risk = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence_score) FROM verifications WHERE is_verified = 1")
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Recent activity (last 24h)
        cursor.execute("""
            SELECT COUNT(*) FROM verifications 
            WHERE timestamp > datetime('now', '-1 day')
        """)
        last_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_verifications': total,
            'verified_count': verified,
            'unverified_count': total - verified,
            'high_risk_count': high_risk,
            'success_rate': (verified / total * 100) if total > 0 else 0,
            'average_confidence': round(avg_confidence, 2),
            'last_24h': last_24h
        }
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search verifications by name, issuer, or certificate ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM verifications
            WHERE student_name LIKE ? 
               OR issuer LIKE ?
               OR certificate_id LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (search_term, search_term, search_term, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Singleton instance
_history_instance: Optional[VerificationHistory] = None

def get_history() -> VerificationHistory:
    global _history_instance
    if _history_instance is None:
        _history_instance = VerificationHistory()
    return _history_instance
