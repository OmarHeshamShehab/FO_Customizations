# D365 Finance and Operations Customizations (FO Customization)

This repository, developed under the acronym **OHMS** (Omar Hesham Mohamed Shehab), serves as a collection of customizations for D365 Finance and Operations. It includes bespoke solutions crafted for various clients, as well as tutorials and cookbooks that showcase best practices in tailoring D365 Finance and Operations to meet specific business needs.

## Table of Contents
- [Project Overview](#project-overview)
- [File and Folder Description](#file-and-folder-description)
  - [ConVehicleManagement](#convehiclemanagement)
  - [Halwani](#halwani)
  - [Metadata](#metadata)
  - [Commerce_CustomerListExtension](#commerce_customerlistextension)
  - [Chain_of_Command](#chain_of_command)

---

## Project Overview

The **FO_Customization** repository is a comprehensive resource for customizations built on D365 Finance and Operations (D365FO). It contains various client-specific solutions, along with tutorials and cookbooks that help developers enhance their skills in configuring and tailoring D365FO applications to suit unique business requirements.

These customizations include solutions for specific modules, integrations, and functionalities, helping clients optimize their business operations within the D365 ecosystem.

---

## File and Folder Description

### ConVehicleManagement
- **Description**: This folder contains customizations and configurations related to vehicle management in D365 Finance and Operations. It may include modules for tracking, maintenance scheduling, and other vehicle-related functionalities.

### Halwani
- **Description**: This folder includes customizations tailored for a specific client named Halwani. These customizations likely address unique business processes, reporting needs, or integrations required by the client.

### Metadata
- **Description**: This folder contains metadata files related to the customizations. These files may include details about data models, form layouts, and workflows associated with the custom solutions.

### Commerce_CustomerListExtension
- **Description**: A D365 Commerce extension project that adds a custom **RefNoExt** field to the customer entity, synchronizing data bidirectionally between Headquarters, Channel Database, and POS in real time.
- **Technologies & Languages**:  
  - **X++** for Dynamics 365 FO extensions (data contract, service & seed-data handlers)  
  - **T-SQL** scripts for Channel DB schema, views, and stored procedures  
  - **C#/.NET** for Commerce Runtime request handlers and triggers  
  - **TypeScript & HTML** for POS ViewExtensions (search columns and add/edit controls)  
- **Frameworks**:  
  - Dynamics 365 Commerce SDK (Commerce Scale Unit sample)  
  - POS extensibility framework  

Use this project to see an end-to-end example of extending D365 Commerce, including code samples, deployment scripts, and best practices for real-time data synchronization across the retail channel.  

---

### Chain_of_Command
- **Description**:  
  The **Chain_of_Command** folder contains a collection of examples demonstrating how to use the **Chain of Command (CoC)** mechanism in D365 Finance and Operations.  
  Each example showcases how to safely extend standard application logic without overlayering, following Microsoft’s extensibility best practices.  

- **Contents Include**:  
  - Examples of CoC applied to **classes**, **tables**, **forms**, **data sources**, and other application objects.  
  - Tutorials with explanations, testing steps, and reference README files.  
  - Code samples that add pre- and post-validation logic, field validations, and conditional overrides.  

- **Purpose**:  
  To help developers understand how to extend and modify standard D365FO behavior using CoC, ensuring custom logic runs safely alongside Microsoft’s updates.  

- **Example Topics**:  
  - Adding custom validation to `SalesTableType.validateWrite()`  
  - Extending `MCREndOrder.validate()` to control order closure logic  
  - Demonstrating CoC extensions on **form data sources** and **table methods**  
  - Showing proper use of `next` calls and result handling in CoC  

This project serves as a **learning module** and a **ready-to-use reference** for developers implementing custom business rules in D365 F&O using Chain of Command.

---

**Author:** Omar Hesham Mohamed Shehab  
**Model:** FO_Customization  
**Environment:** D365 Finance & Operations (Contoso demo data)  
**Last Updated:** 2025-10-09  
