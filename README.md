# D365 Finance and Operations Customizations (FO Customization)

This repository, developed under the acronym **OHMS** (Omar Hesham Mohamed Shehab), serves as a collection of customizations for D365 Finance and Operations. It includes bespoke solutions crafted for various clients, as well as tutorials and cookbooks that showcase best practices in tailoring D365 Finance and Operations to meet specific business needs.

## Table of Contents
- [Project Overview](#project-overview)
- [File and Folder Description](#file-and-folder-description)
  - [ConVehicleManagement](#convehiclemanagement)
  - [Halwani](#halwani)
  - [Metadata](#metadata)
  - [Commerce_CustomerListExtension](#commerce_customerlistextension)

## Project Overview

The **FO_Customization** repository is a comprehensive resource for customizations built on D365 Finance and Operations (D365FO). It contains various client-specific solutions, along with tutorials and cookbooks that help developers enhance their skills in configuring and tailoring D365FO applications to suit unique business requirements.

These customizations include solutions for specific modules, integrations, and functionalities, helping clients optimize their business operations within the D365 ecosystem.

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
  - **X++** for Dynamics 365 FO extensions (data contract, service & seed‑data handlers)  
  - **T‑SQL** scripts for Channel DB schema, views, and stored procedures  
  - **C#/.NET** for Commerce Runtime request handlers and triggers  
  - **TypeScript & HTML** for POS ViewExtensions (search columns and add/edit controls)  
- **Frameworks**:  
  - Dynamics 365 Commerce SDK (Commerce Scale Unit sample)  
  - POS extensibility framework  

Use this project to see an end‑to‑end example of extending D365 Commerce, including code samples, deployment scripts, and best practices for real‑time data synchronization across the retail channel.  
