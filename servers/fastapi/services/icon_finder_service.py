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
                    icons_data = json.load(f)
                    # Extract icons from the complex structure
                    self._icons_cache = {}
                    if "icons" in icons_data:
                        for icon in icons_data["icons"]:
                            icon_name = icon.get("name", "")
                            tags = icon.get("tags", "").split(",") if icon.get("tags") else []
                            # Add the icon name itself as a tag
                            tags.append(icon_name)
                            # Clean up tags
                            tags = [tag.strip() for tag in tags if tag.strip()]
                            self._icons_cache[icon_name] = tags
            except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
                print(f"⚠️ ICON SERVICE: Error loading icons.json: {e}")
                # Return a default set of icons if the file doesn't exist or is malformed
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
        
        # Search through icon names and their tags
        matching_icons = []
        for icon_name, tags in icons_data.items():
            # Check if query matches icon name or any of its tags
            if (query_lower in icon_name.lower() or 
                any(query_lower in tag.lower() for tag in tags)):
                matching_icons.append(icon_name)
        
        # If no matches found, return some default icons
        if not matching_icons:
            matching_icons = ["search", "info", "star", "check"]
        
        return matching_icons[:limit]

# Global instance
ICON_FINDER_SERVICE = IconFinderService()
