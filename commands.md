# 1. Clone and setup
git clone <your-repo>
cd pet-project
cp .env.example .env
# Edit .env with your configurations

# 2. Setup primary server
./deploy/setup_server.sh

# 3. Setup backup server
scp -r . root@backup-server:/app/
ssh root@backup-server "cd /app && ./deploy/setup_server.sh"

# 4. Setup database server
ssh root@db-server "
  apt-get update
  apt-get install -y postgresql postgresql-contrib
  # Configure PostgreSQL
"

# 5. Test the system
curl http://yourdomain.com/health