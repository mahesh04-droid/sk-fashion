# 🚀 How to Deploy Sadguru Krupa on PythonAnywhere (Step-by-Step)

This guide walks you through deploying **Sadguru Krupa** to [PythonAnywhere](https://www.pythonanywhere.com/) using your GitHub repository:
👉 `https://github.com/mahesh04-droid/sk-fashion.git`

---

## 📋 Step 1: Open a Bash Console on PythonAnywhere

1. Log in to your [PythonAnywhere Dashboard](https://www.pythonanywhere.com/).
2. Click on the **Consoles** tab at the top.
3. Under **Start a new console**, click on **Bash**.

---

## 📥 Step 2: Clone Your Repository

In the black Bash console window, run:

```bash
git clone https://github.com/mahesh04-droid/sk-fashion.git
cd sk-fashion
```

---

## 🐍 Step 3: Create & Activate a Virtual Environment

Run:

```bash
python3 -m venv venv
source venv/bin/activate
```

*(You will see `(venv)` appear at the start of your terminal prompt).*

Now install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🗄️ Step 4: Run Migrations, Seed Catalog & Collect Static Files

In the same Bash console, run:

```bash
# 1. Apply database tables
python manage.py migrate

# 2. Seed Ahilyanagar menswear products, banners, and categories
python seed_data.py

# 3. Create your store admin login
python manage.py createsuperuser

# 4. Compile all static stylesheets and scripts
python manage.py collectstatic --noinput
```

*(Note your username and password for the admin login).*

---

## 🌐 Step 5: Configure the Web App on PythonAnywhere

1. In the top navigation bar of PythonAnywhere, click the **Web** tab.
2. Click the **"Add a new web app"** button.
3. Click **Next** on the domain name step (*it will be `yourusername.pythonanywhere.com`*).
4. When asked to "Select a Python Web-Framework", select **"Manual configuration"** *(do NOT select Django, because we already created our own project!)*.
5. Select **Python 3.10** (or 3.11 / 3.12).
6. Click **Next** to finish creating the web app.

---

## ⚙️ Step 6: Configure Paths & WSGI File

Now you will be on your Web App configuration page:

### 1. Set Virtualenv Path
Scroll down to the **Virtualenv** section:
- Click the path area and enter:
  ```text
  /home/YOUR_USERNAME/sk-fashion/venv
  ```
  *(Replace `YOUR_USERNAME` with your actual PythonAnywhere username)*.
- Click the blue checkmark.

### 2. Set Code Paths
In the **Code** section:
- **Source code**: `/home/YOUR_USERNAME/sk-fashion`
- **Working directory**: `/home/YOUR_USERNAME/sk-fashion`

### 3. Edit WSGI Configuration File
In the **Code** section, click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`).

1. Delete everything currently inside that file.
2. Paste the following configuration:

```python
import os
import sys

# Path to your project folder
path = '/home/YOUR_USERNAME/sk-fashion'
if path not in sys.path:
    sys.path.append(path)

# Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'sk_fashion.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Make sure to replace `YOUR_USERNAME` with your PythonAnywhere username!)*

3. Click the green **"Save"** button at the top right, then go back to the **Web** tab.

### 4. Configure Static and Media Files
Scroll down to the **Static files** section on the Web tab. Add the following two rows:

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/sk-fashion/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/sk-fashion/media` |

---

## 🎉 Step 7: Reload & Launch!

Scroll to the very top of the **Web** tab and click the big green **"Reload yourusername.pythonanywhere.com"** button.

Now click your web app link:
👉 `https://yourusername.pythonanywhere.com/`

Your **Sadguru Krupa** store is now live on the internet! 🚀
