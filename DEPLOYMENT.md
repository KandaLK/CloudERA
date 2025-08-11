# 🚀 Cloud ERA Deployment Guide

This guide covers how to deploy Cloud ERA in various environments using the restructured, production-ready architecture.

## 📋 Prerequisites

### Required
- **Docker** 20.10+ and **Docker Compose** v2.0+
- **Node.js** 18+ (for local development)
- **Git** for version control

### API Keys (Recommended)
- **OpenAI API Key** - For AI conversations
- **Tavily API Key** - For web search (optional)
- **JINA AI API Key** - For content scraping (optional)

## 🏗️ Project Structure

After restructuring, the project now has a clean, production-ready structure:

```
AI_Project/
├── src/                          # Frontend source code
│   ├── components/              # React components
│   ├── pages/                   # Page components
│   ├── hooks/                   # Custom hooks
│   ├── services/               # API services
│   ├── types/                  # TypeScript types
│   ├── utils/                  # Utility functions
│   ├── assets/                 # Static assets
│   └── styles/                 # CSS files
├── backend/                     # Backend API
├── public/                      # Public assets
├── dist/                        # Built frontend (after build)
├── docker-compose.yml           # Production deployment
├── docker-compose.dev.yml       # Development deployment
├── Dockerfile                   # Frontend container
├── nginx.conf                   # Production web server config
└── Environment files            # Configuration
```

## 🐳 Production Deployment

### Step 1: Environment Configuration

1. **Copy environment templates:**
   ```bash
   cp .env.production .env
   cp .env.local.example .env.local
   cp backend/.env.example backend/.env
   ```

2. **Configure production environment (`.env`):**
   ```env
   # Required
   VITE_API_BASE_URL=https://your-api-domain.com
   SECRET_KEY=your-super-secure-secret-key-32-chars-minimum
   NEO4J_PASSWORD=your-strong-neo4j-password
   
   # AI Services (recommended)
   OPENAI_API_KEY=your-openai-api-key
   TAVILY_API_KEY=your-tavily-api-key
   JINA_API_KEY=your-jina-api-key
   
   # Optional customization
   MAX_CONCURRENT_USERS=10
   VITE_APP_NAME="Your Company - Cloud ERA"
   ```

### Step 2: Deploy with Docker Compose

1. **Production deployment:**
   ```bash
   docker-compose up -d --build
   ```

2. **Verify deployment:**
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   
   # Health checks
   curl http://localhost/health
   curl http://localhost:8000/health
   ```

### Step 3: Access Points

- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j/your-password)

## 🛠️ Development Deployment

### Local Development (Recommended)

1. **Frontend development:**
   ```bash
   npm install
   cp .env.local.example .env.local
   npm run dev
   ```

2. **Backend development (separate terminal):**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

### Development with Docker

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Access points
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## 🌐 Web Server Configuration

### Nginx (Included)
The project includes optimized Nginx configuration with:
- **Gzip compression** for smaller file sizes
- **Security headers** for protection
- **Caching rules** for performance
- **SPA routing** for React Router
- **Health checks** for monitoring

### Custom Domain Setup

1. **Update environment variables:**
   ```env
   VITE_API_BASE_URL=https://api.yourdomain.com
   ```

2. **Configure reverse proxy (if using separate domains):**
   ```nginx
   server {
       server_name yourdomain.com;
       location / {
           proxy_pass http://localhost:80;
       }
   }
   
   server {
       server_name api.yourdomain.com;
       location / {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## 🔐 Security Configuration

### SSL/HTTPS Setup

1. **Using Let's Encrypt with Nginx:**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Obtain SSL certificate
   sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
   ```

2. **Update Docker Compose for HTTPS:**
   ```yaml
   frontend:
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - /etc/letsencrypt:/etc/letsencrypt:ro
   ```

### Environment Security

- Use **strong secret keys** (32+ characters)
- **Never commit** API keys to version control
- Use **environment-specific** configuration files
- Implement **IP restrictions** if needed

## 📊 Monitoring & Health Checks

### Built-in Health Checks

- **Frontend**: `GET /health` → Returns "healthy"
- **Backend**: `GET /health` → Returns status info
- **Neo4j**: Connection health via backend
- **Agent Status**: `GET /api/chat/agent-status` → System metrics

### Monitoring Commands

```bash
# Check all container health
docker-compose ps

# View real-time logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Check Neo4j status
docker exec cloud-era-neo4j cypher-shell "CALL dbms.cluster.overview()"
```

## 🔄 Updates & Maintenance

### Updating the Application

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

3. **Update dependencies (if needed):**
   ```bash
   # Frontend
   npm update
   
   # Backend
   cd backend && pip install -r requirements.txt --upgrade
   ```

### Database Backup

```bash
# Backup SQLite database
docker cp cloud-era-backend:/app/cloud_era.db ./backup-$(date +%Y%m%d).db

# Backup Neo4j data
docker exec cloud-era-neo4j neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/backup-$(date +%Y%m%d).dump
```

## 🐛 Troubleshooting

### Common Issues

1. **Container won't start:**
   ```bash
   # Check logs
   docker-compose logs <service-name>
   
   # Rebuild from scratch
   docker-compose down -v
   docker-compose up --build
   ```

2. **API connection issues:**
   - Verify `VITE_API_BASE_URL` matches backend URL
   - Check CORS configuration in backend
   - Ensure no firewall blocking ports

3. **Neo4j connection issues:**
   - Verify Neo4j credentials
   - Check if Neo4j container is healthy
   - Ensure LIGHTRAG_WORKING_DIR permissions

### Performance Optimization

1. **Frontend optimization:**
   - Use production build: `npm run build`
   - Enable Nginx compression
   - Implement CDN for static assets

2. **Backend optimization:**
   - Adjust `MAX_CONCURRENT_USERS` based on server capacity
   - Monitor memory usage with Docker stats
   - Consider PostgreSQL for high-load scenarios

## 🚀 Production Checklist

- [ ] Environment variables configured
- [ ] Strong secret keys generated
- [ ] SSL certificates installed
- [ ] Health checks working
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] DNS records updated
- [ ] Firewall rules configured
- [ ] Log rotation configured
- [ ] Update process documented

## 📞 Support

For deployment issues:
1. Check the logs: `docker-compose logs`
2. Verify environment configuration
3. Test health endpoints
4. Review Docker container status
5. Check network connectivity between services

This deployment guide ensures your Cloud ERA instance runs reliably in production with proper security, monitoring, and maintenance procedures.