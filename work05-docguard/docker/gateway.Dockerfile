FROM gradle:8.11.1-jdk21 AS build
WORKDIR /workspace
COPY gradlew settings.gradle.kts build.gradle.kts ./
COPY gradle gradle
COPY src src
RUN chmod +x gradlew && ./gradlew bootJar -x test --no-daemon

FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=build /workspace/build/libs/*.jar app.jar
COPY config/acl.yaml config/acl.yaml
ENV RETRIEVAL_URL=http://retrieval:8097
ENV ACL_FILE=config/acl.yaml
EXPOSE 8096
CMD ["java", "-jar", "app.jar"]