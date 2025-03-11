Feature: Online Trading Platform API Testing

  # User Onboarding and KYC
  Scenario: Successful user registration with valid email
    Given the API endpoint "/api/v1/registration"
    When I send a POST request with payload:
      """
      {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "mobile": "+1234567890"
      }
      """
    Then the response status should be 201
    And the response should contain "Account created successfully"
    And the response should contain a valid "userId"

  Scenario: Failed registration with existing email
    Given the API endpoint "/api/v1/registration"
    When I send a POST request with payload:
      """
      {
        "email": "existing@example.com",
        "password": "Password123!"
      }
      """
    Then the response status should be 409
    And the response should contain "User already exists"

  # KYC Verification
  Scenario: Successful KYC document upload
    Given the API endpoint "/api/v1/kyc/documents"
    And a valid user authentication token
    When I send a POST request with multipart form data:
      | field    | value           |
      | docType  | PAN             |
      | file     | valid-pan.pdf   |
    Then the response status should be 200
    And the response should contain "Document uploaded successfully"

  # Funds Management
  Scenario: Successful fund deposit via UPI
    Given the API endpoint "/api/v1/funds/deposit"
    And a valid user authentication token
    When I send a POST request with payload:
      """
      {
        "amount": 10000,
        "paymentMethod": "UPI",
        "upiId": "user@upi"
      }
      """
    Then the response status should be 200
    And the response should contain "Transaction successful"
    And the account balance should be updated

  # Trading Functionality
  Scenario: Place market order for stock purchase
    Given the API endpoint "/api/v1/trading/order"
    And a valid user authentication token
    When I send a POST request with payload:
      """
      {
        "symbol": "AAPL",
        "quantity": 10,
        "orderType": "MARKET",
        "transactionType": "BUY"
      }
      """
    Then the response status should be 200
    And the response should contain "Order placed successfully"
    And the order status should be "EXECUTED"

  # Performance Testing
  Scenario: Verify API response time under load
    Given the API endpoint "/api/v1/trading/quotes"
    When I send 1000 concurrent GET requests
    Then all responses should be received within 2 seconds
    And the success rate should be greater than 99%

  # Security Testing
  Scenario: Verify secure data transmission
    Given the API endpoint "/api/v1/user/profile"
    When I send a GET request with invalid authentication token
    Then the response status should be 401
    And the response should contain "Unauthorized access"

  # Edge Cases
  Scenario: Handle order placement during market volatility
    Given the API endpoint "/api/v1/trading/order"
    And market volatility is high
    When I send a POST request with payload:
      """
      {
        "symbol": "TSLA",
        "quantity": 5,
        "orderType": "LIMIT",
        "price": 250.00
      }
      """
    Then the response status should be 200
    And the response should contain circuit breaker status
    And the order should be validated against price bands
