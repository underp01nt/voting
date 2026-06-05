## TEAM AIR - Voting Process
> [!note]
> 
> This application is currently incomplete and in development.
> 

## Quick start

1. ### Clone the repository
```bash
git clone https://github.com/underp01nt/voting.git
```

2. ### Move into the repository
```bash
cd voting
```

3. ### Copy .env.example to .env
```bash
cp .env.example .env
```

4. ### Build and start the required containers
```bash
docker compose up --build
```

5. ### Access the web server
```
127.0.0.1:8000
```

### Testing
- For token generation:
```
127.0.0.1:8000/test-token
```