# 🚀 LAZRPAY - Solana Payment System

> **A Modern, Decentralized Payment Platform Built on Solana Blockchain**

![LAZRPAY Logo](https://media1.tenor.com/m/kqi8vJhT8PoAAAAC/larry-enticer.gif)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Installation & Setup](#-installation--setup)
- [Environment Configuration](#-environment-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [MoonPay Integration](#-moonpay-integration)
- [Database Schema](#-database-schema)
- [Security Features](#-security-features)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## 🌟 Overview

LAZRPAY is a comprehensive payment platform that enables seamless cryptocurrency transactions using the Solana blockchain. The platform allows users to send SOL to anyone via email, with integrated fiat offramping through MoonPay for bank transfers.

### 🎯 Key Capabilities

- **Send SOL**: Transfer Solana tokens to anyone using their email address
- **Receive SOL**: Claim received SOL tokens with secure authentication
- **Fiat Offramping**: Convert SOL to fiat currency via MoonPay integration
- **No Wallet Required**: Recipients don't need a wallet to receive payments
- **Email Notifications**: Automatic email notifications for transactions
- **Modern UI/UX**: Glassmorphism design with dark/light mode support

## ✨ Features

### 🔄 Core Payment Features
- **Email-Based Transfers**: Send SOL using recipient's email address
- **Secure Claiming**: Recipients claim funds with email verification
- **Transaction Tracking**: Real-time transaction status monitoring
- **Multi-Network Support**: Solana Devnet and Mainnet compatibility

### 💳 MoonPay Integration
- **Fiat Conversion**: Convert SOL to INR (Indian Rupees)
- **Bank Transfers**: Direct bank account deposits
- **KYC/AML Compliance**: Built-in regulatory compliance
- **Real-Time Rates**: Live cryptocurrency exchange rates

### 🎨 User Experience
- **Modern UI**: Glassmorphism design with floating elements
- **Dark/Light Mode**: Theme toggle with persistent preferences
- **Responsive Design**: Mobile-first responsive layout
- **Micro-Interactions**: Smooth animations and transitions
- **Accessibility**: WCAG-compliant design standards

### 🔐 Security & Authentication
- **Google OAuth**: Secure social authentication
- **CSRF Protection**: Cross-site request forgery protection
- **Transaction Signing**: Secure Solana transaction signing
- **Webhook Verification**: MoonPay webhook signature validation

## 🛠 Technology Stack

### Backend
- **Django 5.1.5**: Web framework
- **Django REST Framework**: API development
- **Django Allauth**: Authentication system
- **Solana Web3.py**: Blockchain integration
- **SQLite**: Database (development)
- **PostgreSQL**: Database (production ready)

### Frontend
- **HTML5/CSS3**: Markup and styling
- **Tailwind CSS**: Utility-first CSS framework
- **JavaScript (ES6+)**: Client-side functionality
- **Font Awesome 6**: Icon library
- **MoonPay Web SDK**: Fiat conversion integration

### Blockchain
- **Solana**: High-performance blockchain
- **Solana Web3.js**: JavaScript SDK
- **Solana Python SDK**: Python integration
- **Devnet/Mainnet**: Network support

### Third-Party Services
- **MoonPay**: Fiat on/offramping
- **Google OAuth**: Authentication
- **Email Services**: Transaction notifications

## 🏗 Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (Django       │◄──►│   (Django       │◄──►│   (Solana       │
│   Templates)    │    │   REST API)     │    │   Network)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MoonPay       │    │   Database      │    │   Email         │
│   (Fiat         │    │   (SQLite/      │    │   (Transaction  │
│   Conversion)   │    │   PostgreSQL)   │    │   Notifications)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Send Transaction**:
   ```
   User Input → Django View → Solana Transaction → Database → Email Notification
   ```

2. **Claim Transaction**:
   ```
   Email Link → Authentication → MoonPay SDK → SOL Transfer → Bank Deposit
   ```

3. **MoonPay Integration**:
   ```
   Claim Request → MoonPay Widget → KYC/AML → Wallet Generation → SOL Transfer → Fiat Conversion
   ```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Solana CLI tools
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd lazr
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (if needed)
npm install
```

### Step 3: Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Solana Configuration
PRIVATE_KEY_BASE58=your-solana-private-key-base58
SOLANA_NETWORK=devnet

# MoonPay Configuration
MOONPAY_API_KEY=pk_test_DjAai22vaOAHWsftWvsyvjD6JUymlz
MOONPAY_SECRET_KEY=your-moonpay-secret-key
MOONPAY_WEBHOOK_SECRET=your-webhook-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## ⚙️ Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `PRIVATE_KEY_BASE58` | Solana wallet private key | `4xQy...` |
| `MOONPAY_API_KEY` | MoonPay public API key | `pk_test_...` |
| `MOONPAY_SECRET_KEY` | MoonPay secret key | `sk_test_...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123456789.apps.googleusercontent.com` |
| `EMAIL_HOST_USER` | Email service username | `your-email@gmail.com` |

### Solana Network Configuration

- **Devnet**: For testing and development
- **Mainnet**: For production transactions

## 📱 Usage

### Sending SOL

1. **Navigate to Send Page**: Visit `/welcome`
2. **Enter Recipient Details**:
   - Recipient Email
   - SOL Amount
   - Reference (optional)
3. **Connect Wallet**: Link your Solana wallet
4. **Confirm Transaction**: Review and send

### Receiving SOL

1. **Check Email**: Look for transaction notification
2. **Click Claim Link**: Follow the secure link
3. **Authenticate**: Sign in with Google account
4. **Choose Option**:
   - **Direct Claim**: Receive SOL to your wallet
   - **Bank Transfer**: Convert to fiat via MoonPay

### MoonPay Bank Transfer

1. **Select Bank Transfer**: Choose fiat conversion option
2. **Complete KYC**: Provide identification documents
3. **Enter Bank Details**: Add your bank account information
4. **Confirm Transfer**: Review and confirm the transaction
5. **Receive Funds**: Funds deposited to your bank account

## 🔌 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page |
| `GET` | `/welcome` | Send crypto page |
| `GET` | `/receive_main/` | Receive main page |
| `POST` | `/logout` | User logout |

### Transaction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sol/send/` | Send SOL transaction |
| `GET` | `/receive/` | Claim specific transaction |
| `GET` | `/moonpay-claim/` | MoonPay claim page |
| `GET` | `/deposit-success/` | Deposit success page |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sender/create/` | Create sender |
| `GET` | `/senders/` | List all senders |
| `POST` | `/recipient/create/` | Create recipient |
| `GET` | `/recipients/` | List all recipients |
| `POST` | `/transaction/create/` | Create transaction |
| `GET` | `/transactions/` | List all transactions |
| `PUT` | `/update/status/<tx_hash>/` | Update transaction status |

### MoonPay Integration Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/moonpay/simulate-deposit/` | Simulate MoonPay deposit |
| `POST` | `/moonpay/webhook/` | MoonPay webhook handler |
| `POST` | `/moonpay/test-webhook/` | Test webhook endpoint |

## 🌙 MoonPay Integration

### How It Works

1. **User Initiates Claim**: Clicks "Start Bank Transfer"
2. **MoonPay Widget Opens**: SDK loads in overlay
3. **KYC/AML Process**: User completes verification
4. **Bank Details Collection**: User enters account information
5. **Deposit Address Generation**: MoonPay generates unique wallet
6. **SOL Transfer**: System sends SOL to MoonPay's wallet
7. **Fiat Conversion**: MoonPay converts SOL to INR
8. **Bank Transfer**: Funds deposited to user's account

### Technical Implementation

```javascript
// MoonPay SDK Integration
const widget = moonPay({
    flow: "sell",
    environment: "sandbox",
    params: {
        apiKey: "pk_test_DjAai22vaOAHWsftWvsyvjD6JUymlz",
        baseCurrencyCode: "sol",
        baseCurrencyAmount: amount,
        defaultCurrencyCode: "inr",
        externalTransactionId: txHash,
        email: email,
        lockAmount: true
    },
    handlers: {
        onInitiateDeposit: function(depositDetails) {
            // Handle deposit initiation
            var walletAddress = depositDetails.depositWalletAddress;
            // Send SOL to MoonPay's wallet
        },
        onTransactionCompleted: function(transaction) {
            // Handle completion
        }
    }
});
```

### Webhook Processing

```python
@csrf_exempt
def moonpay_webhook(request):
    # Verify webhook signature
    # Process transaction status updates
    # Update local database
    # Send notifications
```

## 🗄️ Database Schema

### Models

#### Sender Model
```python
class Sender(models.Model):
    sender_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=44, unique=True)
```

#### Recipient Model
```python
class Recipient(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
```

#### Transaction Model
```python
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('failed', 'failed'),
    ]
    
    tx_id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(Sender, on_delete=models.CASCADE)
    to_receiver = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    tx_hash = models.CharField(max_length=500, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=9)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
```

### Relationships

- **Sender** ↔ **User**: One-to-one relationship
- **Sender** → **Transaction**: One-to-many (sent transactions)
- **Recipient** → **Transaction**: One-to-many (received transactions)

## 🔒 Security Features

### Authentication & Authorization
- **Google OAuth 2.0**: Secure social authentication
- **Session Management**: Django session handling
- **Permission Checks**: Transaction ownership verification
- **CSRF Protection**: Cross-site request forgery prevention

### Blockchain Security
- **Private Key Management**: Secure key storage
- **Transaction Signing**: Cryptographic signature verification
- **Network Validation**: Solana network confirmation
- **Hash Verification**: Transaction hash validation

### API Security
- **Rate Limiting**: Request throttling
- **Input Validation**: Data sanitization
- **Webhook Verification**: MoonPay signature validation
- **Error Handling**: Secure error responses

### Data Protection
- **Encryption**: Sensitive data encryption
- **Access Control**: Role-based permissions
- **Audit Logging**: Transaction tracking
- **Backup Security**: Secure data backups

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
   ```bash
   # Set production environment variables
   export DEBUG=False
   export ALLOWED_HOSTS=your-domain.com
   export DATABASE_URL=postgresql://user:pass@host:port/db
   ```

2. **Database Migration**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

3. **Web Server Configuration**:
   ```bash
   # Using Gunicorn
   gunicorn lazr.wsgi:application --bind 0.0.0.0:8000
   ```

4. **Reverse Proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "lazr.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🤝 Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your feature
4. **Test Thoroughly**: Ensure all tests pass
5. **Submit Pull Request**: Create detailed PR description

### Code Standards

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ standards
- **HTML/CSS**: Follow semantic markup principles
- **Documentation**: Update README for new features

### Testing

```bash
# Run Django tests
python manage.py test

# Run specific test
python manage.py test myapp.tests.TestTransactionFlow
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

**Made By Sri Guhan and Avighna Basak**

## 🙏 Acknowledgments

- **Solana Foundation**: For the Solana blockchain
- **MoonPay**: For fiat conversion services
- **Django Community**: For the excellent web framework
- **Tailwind CSS**: For the utility-first CSS framework

## 📞 Support

For support and questions:
- **Email**: [your-email@domain.com]
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

---

**🚀 Ready to revolutionize payments with Solana!**

