from typing import List
import os
import json

class IconFinderService:
    """Simple icon finder service that returns placeholder icons"""
    
    def __init__(self):
        self.icons_path = os.path.join(os.path.dirname(__file__), "..", "static", "icons")
        self.icons_data_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons.json")
        self._icons_cache = None
    
    def _load_icons(self):
        """Load icons from the icons.json file"""
        if self._icons_cache is None:
            try:
                with open(self.icons_data_path, 'r') as f:
                    self._icons_cache = json.load(f)
            except FileNotFoundError:
                # Return a default set of icons if the file doesn't exist
                self._icons_cache = {
                    "search": ["search", "magnifying-glass", "find"],
                    "user": ["user", "person", "profile"],
                    "home": ["home", "house"],
                    "settings": ["settings", "gear", "cog"],
                    "download": ["download", "arrow-down"],
                    "upload": ["upload", "arrow-up"],
                    "edit": ["edit", "pencil", "modify"],
                    "delete": ["delete", "trash", "remove"],
                    "add": ["add", "plus", "create"],
                    "close": ["close", "x", "cancel"],
                    "save": ["save", "floppy", "disk"],
                    "print": ["print", "printer"],
                    "email": ["email", "mail", "envelope"],
                    "phone": ["phone", "telephone", "call"],
                    "calendar": ["calendar", "date", "schedule"],
                    "clock": ["clock", "time", "hour"],
                    "star": ["star", "favorite", "bookmark"],
                    "heart": ["heart", "love", "like"],
                    "warning": ["warning", "alert", "caution"],
                    "info": ["info", "information", "help"],
                    "check": ["check", "tick", "done"],
                    "arrow": ["arrow", "direction", "point"],
                    "chart": ["chart", "graph", "analytics"],
                    "trending": ["trending", "growth", "increase"],
                    "costs": ["costs", "money", "price"],
                    "efficiency": ["efficiency", "optimization", "performance"]
                }
        return self._icons_cache
    
    async def search_icons(self, query: str, limit: int = 20) -> List[str]:
        """Search for icons based on query"""
        icons_data = self._load_icons()
        query_lower = query.lower()
        
        # Simple search through icon categories
        matching_icons = []
        for category, keywords in icons_data.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_icons.append(category)
        
        # If no matches found, return some default icons
        if not matching_icons:
            matching_icons = ["search", "info", "star", "check"]
        
        return matching_icons[:limit]

# Global instance
ICON_FINDER_SERVICE = IconFinderService()
