
import strawberry


@strawberry.type
class MessageResponse:
    operation:str
    content: str
    recipient: str
    sender: str
  
    

@strawberry.type
class Message:
    sender: str
    recipient: str
    content: str

@strawberry.type
class Incoming:
    _id: str
    sender: str
    content: str

@strawberry.type
class Outgoing:
    _id: str
    recipient: str
    content: str