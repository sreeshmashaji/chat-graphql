import asyncio
from typing import List, Dict, AsyncGenerator
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL
from database import db
import schema
# MongoDB collection
collection = db.messages




# @strawberry.type
# class MessageResponse:
#     operation:str
#     content: str
#     recipient: str
#     sender: str
  
    

# @strawberry.type
# class Message:
#     sender: str
#     recipient: str
#     content: str

# @strawberry.type
# class Incoming:
#     _id: str
#     sender: str
#     content: str

# @strawberry.type
# class Outgoing:
#     _id: str
#     recipient: str
#     content: str

# Active subscriptions dictionary
active_subscriptions: Dict[str, List[asyncio.Queue[schema.Message]]] = {}

@strawberry.type
class Query:
    @strawberry.field
    def all_incoming_messages(self, username: str) -> List[schema.Incoming]:
        incoming_messages = list(collection.find({'recipient': username}))
        for i in incoming_messages:
            i["_id"] = str(i["_id"])
            i.pop("recipient")
        return [schema.Incoming(**doc) for doc in incoming_messages]

    @strawberry.field
    def all_outgoing_messages(self, username: str) -> List[schema.Outgoing]:
        outgoing_messages = list(collection.find({'sender': username}))
        for i in outgoing_messages:
            i["_id"] = str(i["_id"])
            i.pop("sender")
        return [schema.Outgoing(**doc) for doc in outgoing_messages]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def send_message(self, sender: str, recipient: str, content: str) -> schema.Message:
        message = schema.Message(sender=sender, recipient=recipient, content=content)
        collection.insert_one(message.__dict__)

        # Notify all subscribers of the recipient
        if recipient in active_subscriptions:
            for queue in active_subscriptions[recipient]:
                asyncio.create_task(queue.put(message))
        
        # Notify the sender as well (if needed)
        if sender in active_subscriptions:
            for queue in active_subscriptions[sender]:
                asyncio.create_task(queue.put(message))

        return message

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def new_message(self, username: str) -> AsyncGenerator[schema.MessageResponse, None]:
        if username not in active_subscriptions:
            active_subscriptions[username] = []

        # Create an async queue for this subscription
        queue = asyncio.Queue()
        active_subscriptions[username].append(queue)
        
        try:
            while True:
                message = await queue.get() 
                print("message",message) # Get message from the queue
                if message.sender==username:
                    print("here")
                    new_message=schema.MessageResponse(operation="sent",content=message.content,recipient=message.recipient,sender=message.sender)
                if message.recipient==username:
                    new_message=schema.MessageResponse(operation="Recieved",content=message.content,recipient=message.recipient,sender=message.sender)
                    
       
                yield new_message
        except asyncio.CancelledError:
            # Remove the queue if subscription is canceled
            active_subscriptions[username].remove(queue)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

app = FastAPI()
graphql_app = GraphQLRouter(schema,graphql_ide="apollo-sandbox", subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL])
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI with Strawberry!"}
