from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="", tags=["welcome"])


@router.get("/", response_class=HTMLResponse)
async def welcome():
    """
    Welcome page with language switcher and API documentation links.
    Supports English, Russian, and Uzbek languages.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Authentication Module</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                color: #333;
            }

            header {
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                padding: 1.5rem 2rem;
                position: sticky;
                top: 0;
                z-index: 100;
            }

            .header-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }

            .header-title {
                font-size: 1.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .language-switcher {
                display: flex;
                gap: 0.5rem;
            }

            .lang-btn {
                padding: 0.5rem 1rem;
                border: 2px solid #667eea;
                background: white;
                color: #667eea;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }

            .lang-btn:hover {
                background: #f0f4ff;
                transform: translateY(-2px);
            }

            .lang-btn.active {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-color: transparent;
            }

            main {
                flex: 1;
                max-width: 1200px;
                margin: 0 auto;
                width: 100%;
                padding: 3rem 2rem;
            }

            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }

            .hero {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 3rem 2rem;
                text-align: center;
            }

            .hero h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                font-weight: 700;
            }

            .hero p {
                font-size: 1.1rem;
                opacity: 0.95;
                max-width: 600px;
                margin: 0 auto;
                line-height: 1.6;
            }

            .content {
                padding: 3rem 2rem;
            }

            .section {
                margin-bottom: 3rem;
            }

            .section:last-child {
                margin-bottom: 0;
            }

            .section h2 {
                font-size: 1.8rem;
                margin-bottom: 1.5rem;
                color: #333;
                border-bottom: 3px solid #667eea;
                padding-bottom: 0.5rem;
                display: inline-block;
            }

            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
            }

            .feature-card {
                background: #f8f9ff;
                padding: 2rem;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
            }

            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
            }

            .feature-card h3 {
                color: #667eea;
                margin-bottom: 0.5rem;
                font-size: 1.1rem;
            }

            .feature-card p {
                color: #666;
                line-height: 1.6;
                font-size: 0.95rem;
            }

            .docs-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }

            .doc-link {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }

            .doc-link:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
            }

            footer {
                background: rgba(0, 0, 0, 0.1);
                color: white;
                text-align: center;
                padding: 2rem;
                margin-top: auto;
            }

            footer p {
                font-size: 0.9rem;
                opacity: 0.9;
            }

            .hidden {
                display: none;
            }

            @media (max-width: 768px) {
                .header-container {
                    flex-direction: column;
                    align-items: flex-start;
                }

                .hero h1 {
                    font-size: 1.8rem;
                }

                .hero p {
                    font-size: 1rem;
                }

                .section h2 {
                    font-size: 1.5rem;
                }

                main {
                    padding: 1.5rem 1rem;
                }

                .content {
                    padding: 1.5rem 1rem;
                }

                .hero {
                    padding: 2rem 1rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="header-container">
                <div class="header-title" data-lang="en">Quiz Authentication Module</div>
                <div class="header-title hidden" data-lang="ru">Модуль Аутентификации для Викторин</div>
                <div class="header-title hidden" data-lang="uz">Viktorina Autentifikatsiya Moduli</div>
                <div class="language-switcher">
                    <button class="lang-btn active" id="lang-en">EN</button>
                    <button class="lang-btn" id="lang-ru">RU</button>
                    <button class="lang-btn" id="lang-uz">UZ</button>
                </div>
            </div>
        </header>

        <main>
            <div class="container">
                <div class="hero">
                    <h1 data-lang="en">Welcome to Quiz Authentication Module</h1>
                    <h1 class="hidden" data-lang="ru">Добро пожаловать в Модуль Аутентификации для Викторин</h1>
                    <h1 class="hidden" data-lang="uz">Viktorina Autentifikatsiya Moduliga Xush Kelibsiz</h1>
                    
                    <p data-lang="en">A comprehensive authentication system designed for quiz applications with support for user registration, secure login, and token-based access control.</p>
                    <p class="hidden" data-lang="ru">Комплексная система аутентификации, разработанная для приложений викторин с поддержкой регистрации пользователей, безопасного входа и управления доступом на основе токенов.</p>
                    <p class="hidden" data-lang="uz">Viktorina ilovalariga mo'ljallangan keng qamrovli autentifikatsiya tizimi, foydalanuvchi ro'yxatdan o'tish, xavfsiz kirish va token asosidagi kirish nazoratini qo'llab-quvvatlaydi.</p>
                </div>

                <div class="content">
                    <section class="section">
                        <h2 data-lang="en">Key Features</h2>
                        <h2 class="hidden" data-lang="ru">Основные возможности</h2>
                        <h2 class="hidden" data-lang="uz">Asosiy Xususiyatlar</h2>

                        <div class="features-grid">
                            <div class="feature-card">
                                <h3 data-lang="en">User Registration</h3>
                                <h3 class="hidden" data-lang="ru">Регистрация пользователей</h3>
                                <h3 class="hidden" data-lang="uz">Foydalanuvchi Ro'yxatdan O'tish</h3>
                                
                                <p data-lang="en">Easy and secure user registration with email verification and password validation.</p>
                                <p class="hidden" data-lang="ru">Простая и безопасная регистрация пользователей с проверкой электронной почты и валидацией пароля.</p>
                                <p class="hidden" data-lang="uz">Elektron pochta tekshiruvi va parol tekshiruvi bilan oson va xavfsiz foydalanuvchi ro'yxatdan o'tish.</p>
                            </div>

                            <div class="feature-card">
                                <h3 data-lang="en">Secure Login</h3>
                                <h3 class="hidden" data-lang="ru">Безопасный вход</h3>
                                <h3 class="hidden" data-lang="uz">Xavfsiz Kirish</h3>
                                
                                <p data-lang="en">Robust authentication with encrypted password storage and session management.</p>
                                <p class="hidden" data-lang="ru">Надежная аутентификация с зашифрованным хранилищем паролей и управлением сеансами.</p>
                                <p class="hidden" data-lang="uz">Shifrlangan parol saqlash va sessiya boshqaruvi bilan mustahkam autentifikatsiya.</p>
                            </div>

                            <div class="feature-card">
                                <h3 data-lang="en">Token Management</h3>
                                <h3 class="hidden" data-lang="ru">Управление токенами</h3>
                                <h3 class="hidden" data-lang="uz">Token Boshqaruvi</h3>
                                
                                <p data-lang="en">JWT-based token generation and validation for stateless API authentication.</p>
                                <p class="hidden" data-lang="ru">Генерация и валидация токенов на основе JWT для аутентификации API без состояния.</p>
                                <p class="hidden" data-lang="uz">Stateless API autentifikatsiyasi uchun JWT asosidagi token yaratish va tekshirish.</p>
                            </div>

                            <div class="feature-card">
                                <h3 data-lang="en">Multi-Language Support</h3>
                                <h3 class="hidden" data-lang="ru">Поддержка нескольких языков</h3>
                                <h3 class="hidden" data-lang="uz">Ko'p Tilni Qo'llab-Quvvatlash</h3>
                                
                                <p data-lang="en">Full support for English, Russian, and Uzbek languages with dynamic language switching.</p>
                                <p class="hidden" data-lang="ru">Полная поддержка английского, русского и узбекского языков с динамическим переключением языков.</p>
                                <p class="hidden" data-lang="uz">Ingliz, rus va o'zbek tillarini to'liq qo'llab-quvvatlash va dinamik til almashtirish.</p>
                            </div>
                        </div>
                    </section>

                    <section class="section">
                        <h2 data-lang="en">API Documentation</h2>
                        <h2 class="hidden" data-lang="ru">Документация API</h2>
                        <h2 class="hidden" data-lang="uz">API Hujjatlari</h2>

                        <div class="docs-links">
                            <a href="/docs" class="doc-link" data-lang="en">Swagger UI</a>
                            <a href="/docs" class="doc-link hidden" data-lang="ru">Swagger UI</a>
                            <a href="/docs" class="doc-link hidden" data-lang="uz">Swagger UI</a>
                            
                            <a href="/redoc" class="doc-link" data-lang="en">ReDoc</a>
                            <a href="/redoc" class="doc-link hidden" data-lang="ru">ReDoc</a>
                            <a href="/redoc" class="doc-link hidden" data-lang="uz">ReDoc</a>
                        </div>
                    </section>
                </div>
            </div>
        </main>

        <footer>
            <p data-lang="en">© 2024 Quiz Authentication Module. All rights reserved.</p>
            <p class="hidden" data-lang="ru">© 2024 Модуль Аутентификации для Викторин. Все права защищены.</p>
            <p class="hidden" data-lang="uz">© 2024 Viktorina Autentifikatsiya Moduli. Barcha huquqlar himoyalangan.</p>
        </footer>

        <script>
            const languages = ['en', 'ru', 'uz'];
            let currentLanguage = 'en';

            function switchLanguage(lang) {
                if (!languages.includes(lang)) return;

                currentLanguage = lang;
                localStorage.setItem('preferredLanguage', lang);

                // Hide all elements
                document.querySelectorAll('[data-lang]').forEach(el => {
                    el.classList.add('hidden');
                });

                // Show elements for selected language
                document.querySelectorAll(`[data-lang="${lang}"]`).forEach(el => {
                    el.classList.remove('hidden');
                });

                // Update active button
                document.querySelectorAll('.lang-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.getElementById(`lang-${lang}`).classList.add('active');
            }

            // Initialize language buttons
            languages.forEach(lang => {
                document.getElementById(`lang-${lang}`).addEventListener('click', () => {
                    switchLanguage(lang);
                });
            });

            // Load saved language preference
            const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
            switchLanguage(savedLanguage);
        </script>
    </body>
    </html>
    """
    return html_content
