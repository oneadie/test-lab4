Feature: Advanced Shopping Cart Logic
  Testing complex behaviors: floating points, overwrites, and identity

  Scenario: Buy exact available amount
    Given A product "LastItem" with price 100 and availability 5
    And An empty shopping cart
    When I add product "LastItem" with amount 5 to cart
    Then The cart should contain product "LastItem" with quantity 5

  Scenario: Calculate total with cents
    Given A product "Milk" with price 25.50 and availability 10
    And An empty shopping cart
    When I add product "Milk" with amount 2 to cart
    Then The total cost should be 51.0

  Scenario: Overwrite quantity in cart
    Given A product "Sugar" with price 10 and availability 20
    And An empty shopping cart
    When I add product "Sugar" with amount 5 to cart
    And I add product "Sugar" with amount 10 to cart
    Then The cart should contain product "Sugar" with quantity 10

  Scenario: Add free product
    Given A product "Gift" with price 0 and availability 100
    And An empty shopping cart
    When I add product "Gift" with amount 1 to cart
    Then The total cost should be 0

  Scenario: Product with empty name
    Given A product "" with price 50 and availability 5
    And An empty shopping cart
    When I add product "" with amount 1 to cart
    Then The cart should contain product ""

  Scenario: Same name products collision
    Given A product "Clone" with price 100 and availability 10
    And Another product "Clone" with price 200 and availability 10
    And An empty shopping cart
    When I add product "Clone" (first one) with amount 1 to cart
    Then The cart contains the product regardless of price difference

  Scenario: Remove the only product
    Given A product "T-Shirt" with price 200 and availability 5
    And An empty shopping cart
    When I add product "T-Shirt" with amount 1 to cart
    And I remove product "T-Shirt" from cart
    Then The cart should be empty

  Scenario: Try to buy more than available
    Given A product "Limited" with price 100 and availability 5
    And An empty shopping cart
    When I try to add product "Limited" with amount 6
    Then An error regarding availability should be raised

  Scenario: Inventory deduction check
    Given A product "Bread" with price 10 and availability 10
    And An empty shopping cart
    When I add product "Bread" with amount 3 to cart
    And I submit the order
    Then The product "Bread" availability should be 7

  Scenario: Total for multiple items
    Given An empty shopping cart
    And A product "Pen" with price 10 and availability 100
    And A product "Note" with price 20 and availability 100
    When I add product "Pen" with amount 2 to cart
    And I add product "Note" with amount 3 to cart
    Then The total cost should be 80