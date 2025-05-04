# Solutions to Coding Problems

This repository contains solutions to a series of coding problems. Each problem's solution is located in a separate branch, with explanations and screenshots in this README.

## Repository Structure

* **`main` branch:** Contains general setup instructions and this overall README.
* **`problem-1` branch:** Solution to Problem 1.
* **`problem-2` branch:** Solution to Problem 2.
    ...and so on.

## General Setup Instructions

Before running any of the solutions, you'll need to set up your environment.  It's highly recommended to use a virtual environment to isolate dependencies.

**1. Create and Activate a Virtual Environment (Example using `venv`):**

   ```bash
   python3 -m venv .venv  # Create a virtual environment named ".venv"
   source .venv/bin/activate  # Activate the virtual environment (Linux/macOS)
   # or .venv\Scripts\activate (Windows)
   ```

# Project Setup and Dependencies

This document outlines the setup and installation instructions required to run the project. It includes installing necessary Python packages, system-level dependencies, and configuring a MySQL user.

##  Python Dependencies

The following commands install the required Python packages. It's highly recommended to use a virtual environment to isolate project dependencies.

**1. Install Basic Packages:**

   ```bash
   pip install Faker pandas
   pip install requests pandas streamlit
   pip install SQLAlchemy psycopg2-binary
   pip install PyMySQL
   ```

   * **Explanation:**
        * `Faker`:  Used for generating fake data (e.g., names, addresses) which is helpful for testing.
        * `pandas`:  A powerful library for data manipulation and analysis.
        * `requests`:  A library for making HTTP requests.
        * `streamlit`:  A framework for building interactive web applications in Python.
        * `SQLAlchemy`: A SQL toolkit and Object-Relational Mapper (ORM) that gives the full power and flexibility of SQL.
        * `psycopg2-binary`:  A PostgreSQL adapter for Python. The `-binary` version includes pre-compiled binaries, simplifying installation in some cases.
        * `PyMySQL`:  A MySQL client library written in pure Python.

**2. Install System Dependencies (Linux):**

   These commands install system-level libraries needed for certain Python packages to compile correctly. They are specific to Debian/Ubuntu-based Linux systems.

   ```bash
   sudo apt-get update && sudo apt-get install -y build-essential libssl-dev
   sudo apt-get update && sudo apt-get install -y libpq-dev
   ```

   * **Explanation:**
        * `sudo apt-get update`:  Updates the package lists for upgrades and new packages.
        * `sudo apt-get install -y <package_name>`: Installs the specified package. The `-y` flag automatically answers "yes" to any prompts during the installation.
        * `build-essential`:  A meta-package containing essential tools for compiling software (like gcc, make, and libc).  Often required for installing Python packages with C extensions.
        * `libssl-dev`:  Development files for OpenSSL, a library that provides cryptographic functions (needed for packages like `cryptography`).
        * `libpq-dev`:  Development files for PostgreSQL client libraries (needed for `psycopg2`).

**3. Install Rust (for `streamlit-webrtc`):**

   These commands install Rust, which is a prerequisite for some packages, such as  `streamlit-webrtc`.

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf [https://sh.rustup.rs](https://sh.rustup.rs) | sh
   source $HOME/.cargo/env
   sudo apt-get update && sudo apt-get install -y python3-dev
   ```

   * **Explanation:**
        * `curl ... | sh`:  Downloads and executes the Rust installation script.
        * `source $HOME/.cargo/env`:  Sets up the environment variables needed to use Rust and Cargo (Rust's package manager).
        * `sudo apt-get update && sudo apt-get install -y python3-dev`:  Installs the Python development headers, which may be required when building Python packages that interface with C code.

**4. Upgrade pip and Setuptools:**

   It's a good practice to ensure you have the latest versions of `pip`, `setuptools`, and `wheel`.

   ```bash
   # Make sure you are in your virtual environment (e.g., source /path/to/bin/activate)
   pip install --upgrade pip setuptools wheel
   ```

   * **Explanation:**
        * `pip`:  The package installer for Python.
        * `setuptools`:  A library for packaging Python projects.
        * `wheel`:  A packaging format for Python distributions that aims to be easier to install than source distributions.
        * **Important Note:** The comment emphasizes activating your virtual environment first. This is crucial to avoid conflicts with system-level Python packages. The example path `/path/to/bin/activate` is a placeholder; replace it with the actual path to your virtual environment's activation script.

**5. Install Project Requirements:**

   This command installs all the dependencies listed in the `requirements.txt` file.

   ```bash
   pip install -r /path/to/project/requirements.txt
   ```

   * **Explanation:**
        * `pip install -r <path_to_requirements.txt>`:  Installs all packages specified in the `requirements.txt` file. This file ensures everyone working on the project uses the same package versions.  Replace `/root/mimeng-03/requirements.txt` with the correct path.

**6. Install Additional Packages:**

   ```bash
   pip install --upgrade streamlit-webrtc
   pip install requirements.txt
   ```

   * **Explanation:**
        * `streamlit-webrtc`:  A Streamlit component for real-time video and audio streaming.
        * `pip install requirements.txt`: This line seems to be a duplicate of step 5.  It's worth noting that running it again won't hurt, but it's redundant unless the `requirements.txt` file has been modified in between.

## MySQL User Configuration

These steps describe how to create a new user in MySQL with specific privileges for your database. This is important for security – you generally shouldn't use the root user for your application.

**1. Log in to MySQL:**

   ```bash
   mysql -u root -p
   ```

   * **Explanation:**
        * `mysql`:  The MySQL command-line client.
        * `-u root`:  Specifies the user to log in as (in this case, the root user).  You might need to use a different administrative user if you don't have root access.
        * `-p`:  Prompts for the user's password.

**2. Create the New User:**

   ```sql
   CREATE USER 'new_username'@'localhost' IDENTIFIED BY 'strong_password';
   ```

   * **Explanation:**
        * `CREATE USER`:  A SQL command to create a new user in MySQL.
        * `'new_username'@'localhost'`:  Specifies the username (`new_username`) and the host from which the user is allowed to connect (`localhost`).  `localhost` means the user can only connect from the same machine where MySQL is running.
        * `IDENTIFIED BY 'strong_password'`:  Sets the password for the new user.  **Important:** Replace `'strong_password'` with a real, strong password!

   * **Security Note about Host:**
        * `'new_username'@'%'`:  This alternative syntax allows the user to connect from *any* host.  **This is less secure** and should only be used if absolutely necessary (e.g., if your application is running in a different container or on a different server).  If you use `%`, ensure your firewall is configured to restrict access to the MySQL port (3306) from untrusted sources.

**3. Grant Privileges to the User:**

   ```sql
   GRANT ALL PRIVILEGES ON new_database_name.* TO 'new_username'@'localhost';
   ```

   * **Explanation:**
        * `GRANT ALL PRIVILEGES`:  Assigns all available permissions to the user. This includes `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, etc., on the specified database.
        * `ON new_database_name.*`:  Specifies the database and tables to which the privileges apply.  `new_database_name` is the name of your database, and `.*` means "all tables" within that database.  **Replace `new_database_name` with the actual name of your database.**
        * `TO 'new_username'@'localhost'`:  Specifies the user to whom the privileges are granted.

   * **Security Best Practice:**
        * Instead of `ALL PRIVILEGES`, it's much safer to grant only the necessary privileges. For example:
            ```sql
            GRANT SELECT, INSERT, UPDATE, DELETE ON new_database_name.* TO 'new_username'@'localhost';
            ```
            This grants only the basic data manipulation privileges.

**4. Apply Changes:**

   ```sql
   FLUSH PRIVILEGES;
   ```

   * **Explanation:**
        * `FLUSH PRIVILEGES`:  Reloads the grant tables in MySQL. This ensures that the changes you made to user privileges take effect immediately. Without this, you might have to restart the MySQL server.

**5. Exit MySQL:**

   ```sql
   EXIT;
   ```

   * **Explanation:**
        * `EXIT`:  Closes the MySQL command-line client.

**Important Reminders:**

* **Replace Placeholders:** Always replace placeholders like `'new_username'`, `'strong_password'`, and `new_database_name` with your actual values.
* **Security:** Prioritize security.  Use strong passwords, grant only necessary privileges, and restrict user access to specific hosts whenever possible.
* **Virtual Environments:** Use virtual environments to manage project dependencies and avoid conflicts.
* **Documentation:** Keep your `requirements.txt` file updated to reflect your project's dependencies accurately.
