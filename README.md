# Project description
+Research Problem+: Multi-player game framework to minimize unemployment and poverty while intervening on minimum wage and interest rates.
+Methods+: Model-Based Reinforcement Learning and Adversarial Training
+Data+: Synthetic Data from a built-in parameterized economics simulation data generative model
+Master Thesis: Akshay Gudi
+Advisors HPI+: Prof. Holger Giese, Christian Adriano 
+Advisors SAP: Frank Feinbube

# Endpoints - Web based simulator

1. Create User
    * Method: POST
    * Endpoint: /reg-user
    * Input: ```{ "username":" ", "password":" ", "email":" " }```
    
2. Get API Token
    * Method : GET
    * Endpoint : /token-auth

2. Start Game
    * Method : GET
    * Endpoint: /start-game
    * Authorization: API Key  Token <>

3. Perform Action
    * Method : GET
    * Endpoint: /perform-action/<action-value>
    * Authorization: API Key  Token <>
  
4. End Game
    * Method : GET
    * Endpoint: /end-game
