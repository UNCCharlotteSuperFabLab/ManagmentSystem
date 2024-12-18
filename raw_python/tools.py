from dataclasses import dataclass

@dataclass
class ToolCategory:
    id:int
    name:str
    resources:str
    
    @classmethod
    def from_sql_row(cls, sql_row):
        pass

@dataclass
class Tool:
    id:int
    tool_category:ToolCategory
    name:str
    
    @classmethod
    def from_sql_row(cls, sql_row):
        return cls(sql_row[0], sql_row[1], sql_row[2])

class ToolCategories:
    pass

class Tools:
    pass

