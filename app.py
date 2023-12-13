from typing import List, Union, Any

import strawberry
from strawberry.types import Info
from strawberry.asgi import GraphQL
from strawberry.dataloader import DataLoader, AbstractCache

from redis import Redis


class UserRedisCache(AbstractCache):
    def __init__(self):
        self.redis = Redis(host='redis-cache')

    def get(self, key: Any) -> Union[Any, None]:
        # If cached it should probably return something like User(id=1, name='name') (pickle.loads)
        # but that would cause "'User' object has no attribute 'cancelled'"
        # if not cached, returns None and "works"
        return self.redis.get(key)  # fetch data from persistent cache

    def set(self, key: Any, value: Any) -> None:
        # value is Future without result here - value.result() => "Result is not set."
        # when things are working there might be need for pickle.dumps(value) to be able to restore same type get calling `get`
        self.redis.setex(key, value, 60)  # store data in the cache

    def delete(self, key: Any) -> None:
        self.redis.delete(key)  # delete key from the cache

    def clear(self) -> None:
        self.redis.flushdb()  # clear the cache


@strawberry.type
class User:
    id: strawberry.ID
    name: str


async def load_users(keys) -> List[User]:
    return [User(id=key, name="Jane Doe") for key in keys]


dataloader = DataLoader(load_fn=load_users, cache_map=UserRedisCache())


@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, info: Info, id: strawberry.ID) -> User:
        return await dataloader.load(id)


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)
