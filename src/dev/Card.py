class Card:
    color: str
    sign: str
    
    def __init__(self, color, sign):
        self.color = color
        self.sign = sign
        
    def __str__(self):
        return f"{self.sign} - {self.color}"