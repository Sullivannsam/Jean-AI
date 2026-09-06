# Research: OWASP API Security Top 10

> Auto-researched on 2026-09-02 17:50
> Fetched from source URLs below. Content is unedited extracts.

## Source: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

OWASP Top 10 API Security Risks – 2023 - OWASP API Security Top 10 

 Skip to content

 OWASP API Security Top 10

 OWASP Top 10 API Security Risks – 2023

 Bahasa (Indonesian)

 English

 Français

 Persian

 Português (Portugal)

 Initializing search

 OWASP/API-Security

 Home

 2023

 2019

 OWASP API Security Top 10

 OWASP/API-Security

 Home

 Home

 How-to Contribute

 2023

 2023

 Notice

 Table of Contents

 About OWASP

 Foreword

 Introduction

 Release Notes

 API Security Risks

 OWASP Top 10 API Security Risks – 2023

 API1:2023 Broken Object Level Authorization

 API2:2023 Broken Authentication

 API3:2023 Broken Object Property Level Authorization

 API4:2023 Unrestricted Resource Consumption

 API5:2023 Broken Function Level Authorization

 API6:2023 Unrestricted Access to Sensitive Business Flows

 API7:2023 Server Side Request Forgery

 API8:2023 Security Misconfiguration

 API9:2023 Improper Inventory Management

 API10:2023 Unsafe Consumption of APIs

 What's Next For Developers

 What's Next For DevSecOps

 Methodology and Data

 Acknowledgments

 2019

 2019

 Notice

 Table of Contents

 About OWASP

 Foreword

 Introduction

 Release Notes

 API Security Risks

 OWASP Top 10 API Security Risks – 2019

 API1:2019 Broken Object Level Authorization

 API2:2019 Broken User Authentication

 API3:2019 Excessive Data Exposure

 API4:2019 Lack of Resources & Rate Limiting

 API5:2019 Broken Function Level Authorization

 API6:2019 - Mass Assignment

 API7:2019 Security Misconfiguration

 API8:2019 Injection

 API9:2019 Improper Assets Management

 API10:2019 Insufficient Logging & Monitoring

 What's Next For Developers

 What's Next For DevSecOps

 Methodology and Data

 Acknowledgments

 ## OWASP Top 10 API Security Risks – 2023 Risk Description API1:2023 - Broken Object Level Authorization 
 APIs tend to expose endpoints that handle object identifiers, creating a wide attack surface of Object Level Access Control issues. Object level authorization checks should be considered in every function that accesses a data source using an ID from the user. 

 API2:2023 - Broken Authentication 
 Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise authentication tokens or to exploit implementation flaws to assume other user's identities temporarily or permanently. Compromising a system's ability to identify the client/user, compromises API security overall. 

 API3:2023 - Broken Object Property Level Authorization 
 This category combines API3:2019 Excessive Data Exposure and API6:2019 - Mass Assignment, focusing on the root cause: the lack of or improper authorization validation at the object property level. This leads to information exposure or manipulation by unauthorized parties. 

 API4:2023 - Unrestricted Resource Consumption 
 Satisfying API requests requires resources such as network bandwidth, CPU, memory, and storage. Other resources such as emails/SMS/phone calls or biometrics validation are made available by service providers via API integrations, and paid for per request. Successful attacks can lead to Denial of Service or an increase of operational costs. 

 API5:2023 - Broken Function Level Authorization 
 Complex access control policies with different hierarchies, groups, and roles, and an unclear separation between administrative and regular functions, tend to lead to authorization flaws. By exploiting these issues, attackers can gain access to other users’ resources and/or administrative functions. 

 API6:2023 - Unrestricted Access to Sensitive Business Flows 
 APIs vulnerable to this risk expose a business flow - such as buying a ticket, or posting a comment - without compensating for how the functionality could harm the business if used excessively in an automated manner. This doesn't necessarily come from implementation bugs. 

 API7:2023 - Server Side Request Forgery 
 Server-Side Request Forgery (SSRF) flaws can occur when an API is fetching a remote resource without validating the user-supplied URI. This enables an attacker to coerce the application to send a crafted request to an unexpected destination, even when protected by a firewall or a VPN. 

 API8:2023 - Security Misconfiguration 
 APIs and the systems supporting them typically contain complex configurations, meant to make the APIs more customizable. Software and DevOps engineers can miss these configurations, or don't follow security best practices when it comes to configuration, opening the door for different types of attacks. 

 API9:2023 - Improper Inventory Management 
 APIs tend to expose more endpoints than traditional web applications, making proper and updated documentation highly important. A proper inventory of hosts and deployed API versions also are important to mitigate issues such as deprecated API versions and exposed debug endpoints. 

 API10:2023 - Unsafe Consumption of APIs 
 Developers tend to trust data received from third-party APIs more than user input, and so tend to adopt weaker security standards. In order to compromise APIs, attackers go after integrated third-party services instead of trying to compromise the target API directly. 

 Previous API Security Risks

 Next API1:2023 Broken Object Level Authorization

 © Copyright 2023 - OWASP API Security Project team

 Made with
 Material for MkDocs

## Source: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/

API1:2023 Broken Object Level Authorization - OWASP API Security Top 10 

 Skip to content

 OWASP API Security Top 10

 API1:2023 Broken Object Level Authorization

 Bahasa (Indonesian)

 English

 Français

 Persian

 Português (Portugal)

 Initializing search

 OWASP/API-Security

 Home

 2023

 2019

 OWASP API Security Top 10

 OWASP/API-Security

 Home

 Home

 How-to Contribute

 2023

 2023

 Notice

 Table of Contents

 About OWASP

 Foreword

 Introduction

 Release Notes

 API Security Risks

 OWASP Top 10 API Security Risks – 2023

 API1:2023 Broken Object Level Authorization

 API1:2023 Broken Object Level Authorization

 Table of contents

 Is the API Vulnerable?

 Example Attack Scenarios

 Scenario #1

 Scenario #2

 Scenario #3

 How To Prevent

 References

 OWASP

 External

 API2:2023 Broken Authentication

 API3:2023 Broken Object Property Level Authorization

 API4:2023 Unrestricted Resource Consumption

 API5:2023 Broken Function Level Authorization

 API6:2023 Unrestricted Access to Sensitive Business Flows

 API7:2023 Server Side Request Forgery

 API8:2023 Security Misconfiguration

 API9:2023 Improper Inventory Management

 API10:2023 Unsafe Consumption of APIs

 What's Next For Developers

 What's Next For DevSecOps

 Methodology and Data

 Acknowledgments

 2019

 2019

 Notice

 Table of Contents

 About OWASP

 Foreword

 Introduction

 Release Notes

 API Security Risks

 OWASP Top 10 API Security Risks – 2019

 API1:2019 Broken Object Level Authorization

 API2:2019 Broken User Authentication

 API3:2019 Excessive Data Exposure

 API4:2019 Lack of Resources & Rate Limiting

 API5:2019 Broken Function Level Authorization

 API6:2019 - Mass Assignment

 API7:2019 Security Misconfiguration

 API8:2019 Injection

 API9:2019 Improper Assets Management

 API10:2019 Insufficient Logging & Monitoring

 What's Next For Developers

 What's Next For DevSecOps

 Methodology and Data

 Acknowledgments

 Table of contents

 Is the API Vulnerable?

 Example Attack Scenarios

 Scenario #1

 Scenario #2

 Scenario #3

 How To Prevent

 References

 OWASP

 External

 ## API1:2023 Broken Object Level Authorization Threat agents/Attack vectors Security Weakness Impacts API Specific : Exploitability Easy Prevalence Widespread : Detectability Easy Technical Moderate : Business Specific Attackers can exploit API endpoints that are vulnerable to broken object-level authorization by manipulating the ID of an object that is sent within the request. Object IDs can be anything from sequential integers, UUIDs, or generic strings. Regardless of the data type, they are easy to identify in the request target (path or query string parameters), request headers, or even as part of the request payload. This issue is extremely common in API-based applications because the server component usually does not fully track the client’s state, and instead, relies more on parameters like object IDs, that are sent from the client to decide which objects to access. The server response is usually enough to understand whether the request was successful. Unauthorized access to other users’ objects can result in data disclosure to unauthorized parties, data loss, or data manipulation. Under certain circumstances, unauthorized access to objects can also lead to full account takeover. ## Is the API Vulnerable? Object level authorization is an access control mechanism that is usually implemented at the code level to validate that a user can only access the objects that they should have permissions to access. Every API endpoint that receives an ID of an object, and performs any action on the object, should implement object-level authorization checks. The checks should validate that the logged-in user has permissions to perform the requested action on the requested object. Failures in this mechanism typically lead to unauthorized information disclosure, modification, or destruction of all data. Comparing the user ID of the current session (e.g. by extracting it from the JWT token) with the vulnerable ID parameter isn't a sufficient solution to solve Broken Object Level Authorization (BOLA). This approach could address only a small subset of cases. In the case of BOLA, it's by design that the user will have access to the vulnerable API endpoint/function. The violation happens at the object level, by manipulating the ID. If an attacker manages to access an API endpoint/function they should not have access to - this is a case of Broken Function Level Authorization (BFLA) rather than BOLA. 

## Example Attack Scenarios

## Scenario #1

An e-commerce platform for online stores (shops) provides a listing page with
the revenue charts for their hosted shops. Inspecting the browser requests, an
attacker can identify the API endpoints used as a data source for those charts
and their pattern: /shops/{shopName}/revenue_data.json . Using another API
endpoint, the attacker can get the list of all hosted shop names. With a
simple script to manipulate the names in the list, replacing {shopName} in
the URL, the attacker gains access to the sales data of thousands of e-commerce
stores. 

## Scenario #2

An automobile manufacturer has enabled remote control of its vehicles via a
mobile API for communication with the driver's mobile phone. The API enables
the driver to remotely start and stop the engine and lock and unlock the doors.
As part of this flow, the user sends the Vehicle Identification Number (VIN) to
the API.
The API fails to validate that the VIN represents a vehicle that belongs to the
logged in user, which leads to a BOLA vulnerability. An attacker can access
vehicles that don't belong to him. 

## Scenario #3

An online document storage service allows users to view, edit, store and delete
their documents. When a user's document is deleted, a GraphQL mutation with the
document ID is sent to the API. 

 POST /graphql
{
 "operationName":"deleteReports",
 "variables":{
 "reportKeys":["<DOCUMENT_ID>"]
 },
 "query":"mutation deleteReports($siteId: ID!, $reportKeys: [String]!) {
 {
 deleteReports(reportKeys: $reportKeys)
 }
 }"
}

Since the document with the given ID is deleted without any further permission
checks, a user may be able to delete another user's document. 

## How To Prevent

Implement a proper authorization mechanism that relies on the user policies
 and hierarchy. 

Use the authorization mechanism to check if the logged-in user has access to
 perform the requested action on the record in every function that uses an
 input from the client to access a record in the database. 

Prefer the use of random and unpredictable values as GUIDs for records' IDs. 

Write tests to evaluate the vulnerability of the authorization mechanism. Do
 not deploy changes that make the tests fail. 

## References

## OWASP

Authorization Cheat Sheet 

Authorization Testing Automation Cheat Sheet 

## External

CWE-285: Improper Authorization 

CWE-639: Authorization Bypass Through User-Controlled Key 

 Previous OWASP Top 10 API Security Risks – 2023

 Next API2:2023 Broken Authentication

 © Copyright 2023 - OWASP API Security Project team

 Made with
 Material for MkDocs
