import json
# from collections.abc 
from typing import Any
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer

from app.config import get_settings

DOCUMENT_UPLOADED="document.uploaded"
CHUNKS_CREATED="chunks.created"
EMBEDDINGS_CREATED="embeddings.created"
VECTOR_INDEXED="vector.indexed"

def build_producer()->AIOKafkaProducer:
    settings = get_settings()
    return AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer = lambda value: json.dumps(value).encode("utf-8"),
    )

async def publish(producer: AIOKafkaProducer,topic:str,payload:dict[str,any],key:str|None=None)->None:
    encoded_key= key.encode("utf-8") if key else None
    await producer.send_and_wait(topic,payload,key=encoded_key)

def build_consumer(group_id:str,*topics:str)->AIOKafkaConsumer:
    settings=get_settings()
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

async def consume_messages(consumer:AIOKafkaConsumer)->AsyncIterator[tuple[str,dict[str,Any]]]:
    async for message in consumer:
        yield message.topic,message.value
        await consumer.commit()