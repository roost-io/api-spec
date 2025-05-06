
  package org.springframework.api_tests;

  import com.intuit.karate.Results;
  import com.intuit.karate.Runner;
  // import com.intuit.karate.http.HttpServer;
  // import com.intuit.karate.http.ServerConfig;
  import org.junit.jupiter.api.Test;

  import static org.junit.jupiter.api.Assertions.assertEquals;

  class NobelTest {

      @Test
      void testAll() {
          String apiHostServer = System.getenv().getOrDefault("test_URL_BASE", "http://localhost:4010");
String testauthtoken = System.getenv().getOrDefault("test_AUTH_TOKEN", "dummy_test_AUTH_TOKEN");
          Results results = Runner.path("src/test/java/org/springframework/api_tests/Nobel")
                  .systemProperty("test_URL_BASE", apiHostServer)
.systemProperty("test_AUTH_TOKEN", testauthtoken)
                  .reportDir("testReport").parallel(1);
          assertEquals(0, results.getFailCount(), results.getErrorMessages());
      }

  }
