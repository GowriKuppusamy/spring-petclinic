# Automated Documentation Sync


This document is generated from the repository analysis and content mapping artifacts.

## API Reference

The following endpoints were extracted from the repository analysis artifact.
- **GET** `/owners/new` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **GET** `/owners/find` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **GET** `/owners` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **GET** `/owners/{ownerId}/edit` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **GET** `/owners/{ownerId}` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **POST** `/owners/new` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **POST** `/owners/{ownerId}/edit` — OwnerController (src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- **GET** `/owners/{ownerId}/pets/new` — PetController (src/main/java/org/springframework/samples/petclinic/owner/PetController.java)
- **GET** `/owners/{ownerId}/pets/{petId}/edit` — PetController (src/main/java/org/springframework/samples/petclinic/owner/PetController.java)
- **POST** `/owners/{ownerId}/pets/new` — PetController (src/main/java/org/springframework/samples/petclinic/owner/PetController.java)
- **POST** `/owners/{ownerId}/pets/{petId}/edit` — PetController (src/main/java/org/springframework/samples/petclinic/owner/PetController.java)
- **GET** `/owners/{ownerId}/pets/{petId}/visits/new` — VisitController (src/main/java/org/springframework/samples/petclinic/owner/VisitController.java)
- **POST** `/owners/{ownerId}/pets/{petId}/visits/new` — VisitController (src/main/java/org/springframework/samples/petclinic/owner/VisitController.java)
- **GET** `/oups` — CrashController (src/main/java/org/springframework/samples/petclinic/system/CrashController.java)
- **GET** `/` — WelcomeController (src/main/java/org/springframework/samples/petclinic/system/WelcomeController.java)
- **GET** `/vets.html` — VetController (src/main/java/org/springframework/samples/petclinic/vet/VetController.java)
- **GET** `/vets` — VetController (src/main/java/org/springframework/samples/petclinic/vet/VetController.java)

## Setup and Installation

- Java version: 17
- Build metadata source: pom.xml, build.gradle
- Run the application using the existing project build workflow.

## Environment Configuration

### src/main/resources/application-mysql.properties
- `database` = `mysql`
- `spring.datasource.url` = `${MYSQL_URL:jdbc:mysql://localhost/petclinic}`
- `spring.datasource.username` = `${MYSQL_USER:petclinic}`
- `spring.datasource.password` = `${MYSQL_PASS:petclinic}`
- `spring.sql.init.mode` = `always`

### src/main/resources/application-postgres.properties
- `database` = `postgres`
- `spring.datasource.url` = `${POSTGRES_URL:jdbc:postgresql://localhost/petclinic}`
- `spring.datasource.username` = `${POSTGRES_USER:petclinic}`
- `spring.datasource.password` = `${POSTGRES_PASS:petclinic}`
- `spring.sql.init.mode` = `always`

### src/main/resources/application.properties
- `database` = `h2`
- `spring.sql.init.schema-locations` = `classpath*:db/${database}/schema.sql`
- `spring.sql.init.data-locations` = `classpath*:db/${database}/data.sql`
- `spring.thymeleaf.mode` = `HTML`
- `spring.jpa.hibernate.ddl-auto` = `none`
- `spring.jpa.open-in-view` = `false`
- `spring.jpa.hibernate.naming.physical-strategy` = `org.hibernate.boot.model.naming.PhysicalNamingStrategySnakeCaseImpl`
- `spring.jpa.properties.hibernate.default_batch_fetch_size` = `16`
- `spring.messages.basename` = `messages/messages`
- `management.endpoints.web.exposure.include` = `*`
- `logging.level.org.springframework` = `INFO`
- `spring.web.resources.cache.cachecontrol.max-age` = `12h`


## Change History

- Documentation mapping generated from analysis artifact at: 2026-07-31T15:02:19.487846+00:00
- This section will be expanded by later documentation generation tasks.
