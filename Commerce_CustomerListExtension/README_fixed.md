
# 🚀 Contoso D365 Commerce – RefNoExt Extension

### Overview
This solution extends the standard D365 Commerce Customer entity to include a custom string field **RefNoExt** that can be edited in POS and synchronized back to HQ in real time.

- 📦 Adds `RefNoExt` to **CustTable** via X++ extension  
- 🔄 Propagates changes HQ → Channel DB → POS → HQ  
- 🌱 Implements CDX seed-data extension for initial replication  
- 🛠️ Provides SQL scripts for extension tables, views &amp; procs  
- 💻 Hooks into Commerce Runtime (CRT) to persist &amp; push updates  
- 🛍️ Enhances POS customer search &amp; add/edit forms  

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Solution Structure](#solution-structure)
3. [X++ Extension (HQ)](#x-extension-hq)
4. [Channel Database (Scale Unit)](#channel-database-scale-unit)
5. [Commerce Runtime (CRT) -- C#](#commerce-runtime-crt----c)
6. [POS Customizations](#pos-customizations)
    - [Customer Search Columns](#customer-search-columns)
    - [Customer Add/Edit Control](#customer-addedit-control)
7. [Installation &amp; Deployment](#installation-amp-deployment)
8. [Testing &amp; Verification](#testing-amp-verification)
9. [Contributing](#contributing)
10. [License](#license)

---

## Prerequisites
...

## Contributing
1. Fork repo &amp; create feature branch  
2. Commit changes &amp; push to your fork  
3. Open a Pull Request

---
