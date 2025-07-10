import json
import os
from typing import List

class WhitelistService:
    def __init__(self, whitelist_file_path: str = "whitelist.json"):
        self.whitelist_file_path = whitelist_file_path
        self._ensure_whitelist_file_exists()
    
    def _ensure_whitelist_file_exists(self):
        """Ensure the whitelist file exists, create it if it doesn't"""
        if not os.path.exists(self.whitelist_file_path):
            default_whitelist = {
                "admin_email": "admin@everbloomfinance.com",
                "whitelisted_emails": [
                    "admin@everbloomfinance.com"
                ]
            }
            with open(self.whitelist_file_path, 'w') as f:
                json.dump(default_whitelist, f, indent=2)
    
    def _load_data(self) -> dict:
        """Load the complete data from the JSON file"""
        try:
            with open(self.whitelist_file_path, 'r') as f:
                data = json.load(f)
                # Ensure admin_email exists for backward compatibility
                if "admin_email" not in data:
                    data["admin_email"] = "admin@everbloomfinance.com"
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"admin_email": "admin@everbloomfinance.com", "whitelisted_emails": []}
    
    def _save_data(self, data: dict) -> bool:
        """Save data to the JSON file"""
        try:
            with open(self.whitelist_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def _load_whitelist(self) -> List[str]:
        """Load the whitelist from the JSON file"""
        data = self._load_data()
        return data.get("whitelisted_emails", [])
    
    def get_admin_email(self) -> str:
        """Get the admin email"""
        data = self._load_data()
        return data.get("admin_email", "admin@everbloomfinance.com")
    
    def set_admin_email(self, email: str) -> bool:
        """Set the admin email"""
        data = self._load_data()
        data["admin_email"] = email
        return self._save_data(data)
    
    def is_admin_email(self, email: str) -> bool:
        """Check if an email is the admin email"""
        admin_email = self.get_admin_email()
        return email.lower() == admin_email.lower()
    
    def is_email_whitelisted(self, email: str) -> bool:
        """Check if an email is in the whitelist"""
        whitelist = self._load_whitelist()
        return email.lower() in [e.lower() for e in whitelist]
    
    def add_email_to_whitelist(self, email: str) -> bool:
        """Add an email to the whitelist"""
        data = self._load_data()
        
        if "whitelisted_emails" not in data:
            data["whitelisted_emails"] = []
        
        if email.lower() not in [e.lower() for e in data["whitelisted_emails"]]:
            data["whitelisted_emails"].append(email)
            return self._save_data(data)
        return False
    
    def remove_email_from_whitelist(self, email: str) -> bool:
        """Remove an email from the whitelist"""
        data = self._load_data()
        
        if "whitelisted_emails" not in data:
            return False
        
        original_count = len(data["whitelisted_emails"])
        data["whitelisted_emails"] = [
            e for e in data["whitelisted_emails"] 
            if e.lower() != email.lower()
        ]
        
        if len(data["whitelisted_emails"]) < original_count:
            return self._save_data(data)
        return False
    
    def get_whitelist(self) -> List[str]:
        """Get the current whitelist"""
        return self._load_whitelist()

# Create a global instance
whitelist_service = WhitelistService()