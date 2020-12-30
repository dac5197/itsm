# DACME Technology Service Manager

![Project Image](https://bn1305files.storage.live.com/y4moKmOYScsLgqaAP_3onzaYkb38trWoNBj0AIpD6Ais7WEB7O-9Fa5wpuy6y7CFQqDLSOo0Lkv8AOWsxC6QhIMSh-4Yc8ur4YlzuLLtg8BzGoXhMjjGc4lgwUCjM_c-rbyK1Qwa4J3AVtB6Ya0yqnHm57toS7MrojlPVd_eUv7k8bs8_JhXJH9PdkDdJx2PZGG?width=1114&height=594&cropmode=none)

> Technology Services Manager (TSM) tracks work through tickets.  There are two types of ticket: incidents and requests.  Tickets can be assigned to groups or individuals in those groups.  Tickets have priority ranging from '5 - Low' to '1 - Critical' and follow a status lifecycle that moves from 'created' to 'submitted' to 'in progress' to 'resolved' and finally to 'closed'.

---

### Table of Contents
You're sections headers will be used to reference location of destination.

- [Description](#description)
- [How To Use](#how-to-use)
- [References](#references)
- [License](#license)
- [Author Info](#author-info)

---

## Description

Technology Services Manager (TSM) is my first original project in Python and Django.  After working through several tutorials, I decided the best way to further my knowledge was to build a functional web application.

TSM tracks work through tickets.  There are two types of ticket: incidents and requests.  Incidents are for impairment of existing access or functionality of an account or system.  Requests are for new access or functionality or for modification of such for an account or system.

Built along with TSM was user authentication, group structure, and homepages.  By default, users only have read access on the tickets.  Once added to an assignment group, the user will then have the role that grants write access to create and modify tickets.  

All of the tickets submitted with the user as the customer can be viewed on their homepage.  For TSM assignment group members, additional homepages are available for tickets assigned to that user and tickets assigned to all of the teams that user is a member of.

The groups and sidebar links use Materialized Path Tree (MPT) for setting up the nested structure.  The sidebar links are dynamic based on the logged in user's roles.

#### Technologies

- Python
- Django
- Postgres
- HTML
- CSS
- Javascript
- Bootstrap


[Back To The Top](#dacme-technology-service-manager)

---

## How To Use

Create and work tickets.  

### Installation

[PIP requirements](https://github.com/dac5197/itsm/blob/master/requirements.txt)

[Back To The Top](#dacme-technology-service-manager)

---

## References

Tutorials and other videos I watched to learn Python and Django.  All of these videos were helpful in building this project.

### Dennis Ivy
[Django Ecommerce Website Playlist](https://www.youtube.com/playlist?list=PL-51WBLyFTg0omnamUjL1TCVov7yDTRng)

[To Do App | Django 3.0](https://www.youtube.com/watch?v=4RWFvXDUmjo&t=1s)

### Tech With Tim
[Python As Fast as Possible - Learn Python in ~75 Minutes](https://www.youtube.com/watch?v=VchuKL44s6E)

### Telusko
[Django Tutorial for Beginners | Full Course](https://www.youtube.com/watch?v=OTmQOjsl0eg&t=1183s)

[Back To The Top](#dacme-technology-service-manager)

---

## License

MIT License

Copyright (c) [2020] [Don Chaney]

[LICENSE](https://github.com/dac5197/itsm/blob/master/LISCENSE.md)

[Back To The Top](#dacme-technology-service-manager)

---

## Author Info

- LindedIN - [Don Chaney](https://www.linkedin.com/in/donald-chaney)
- Website - [Don Chaney](#)

[Back To The Top](#dacme-technology-service-manager)


