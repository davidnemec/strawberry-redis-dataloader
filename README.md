- git clone
- docker-compose up
- Go to http://localhost:8000/graphql and run query
```
{
  getUser(id: 1) {
    id
    name
  }
}
```