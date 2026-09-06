# Research: Burp Suite usage

> Auto-researched on 2026-09-02 17:51
> Fetched from source URLs below. Content is unedited extracts.

## Source: https://portswigger.net/burp/documentation/desktop/getting-started

Getting started with Burp Suite Professional / Community Edition - PortSwigger 

 My account

 Products 

 Solutions 

 Research
 Academy

 Support 

 Company 

 Customers
 About
 Blog
 Careers
 Legal
 Contact
 Resellers

 My account
 Customers
 About
 Blog
 Careers
 Legal
 Contact
 Resellers

 Burp AT Agentic AI that extends human-led pentesting.

 Burp Suite DAST The enterprise-enabled dynamic web vulnerability scanner.

 Burp Suite Professional The world's #1 web penetration testing toolkit.

 Burp Suite Community Edition The best manual tools to start web security testing.

 View all product editions

 Burp Scanner Burp Suite's web vulnerability scanner

 Attack surface visibility Improve security posture, prioritize manual testing, free up time.
 CI-driven scanning More proactive security - find and fix vulnerabilities earlier.
 Application security testing See how our software enables the world to secure the web.
 DevSecOps Catch critical bugs; ship more secure software, more quickly.

 Penetration testing Accelerate penetration testing - find more bugs, more quickly.
 Automated scanning Scale dynamic scanning. Reduce risk. Save time/money.

 Bug bounty hunting Level up your hacking and earn more bug bounties.
 Compliance Enhance security monitoring to comply with confidence.

 View all solutions

 Product comparison What's the difference between Pro and DAST?

 Support Center Get help and advice from our experts on all things Burp.
 Documentation Tutorials and guides for Burp Suite.
 Get Started - Professional Get started with Burp Suite Professional.
 Get Started - DAST Get started with Burp Suite DAST.
 Downloads Download the latest version of Burp Suite.

 Visit the Support Center

 Downloads Download the latest version of Burp Suite.

 Product Support and Documentation 

 Support Center

 Getting Started 

 Professional/Community Edition
 Burp Suite DAST

 Latest Releases

 Extend Burp 

 BApp Store
 Extensions
 Bambdas
 Custom scan checks

 Training

 Back to documentation home

## Professional and Community Edition

 Professional and Community Edition

 Getting started

 System requirements

 Step 1: Download and install

 Step 2: Intercepting HTTP traffic

 Step 3: Modifying requests

 Step 4: Setting the target scope

 Step 5: Reissuing requests

 Step 6: Running your first scan [Pro only]

 Step 7: Generating a report [Pro only]

 Step 8: What next?

 Testing workflow

 Setting the test scope

 Mapping the website

 Mapping the visible attack surface

 Discovering hidden content

 Automated content discovery

 Hostname discovery

 Analyzing the attack surface

 Scoping the effort to audit a website

 Identifying high-risk functionality

 Identifying supported HTTP methods

 Checking for hidden inputs

 Evaluating inputs

 Analyzing opaque data

 Decoding opaque data

 Identifying which parts of a token impact the response

 Testing for vulnerabilities

 Testing authentication mechanisms

 Enumerating usernames

 Guessing usernames for known users

 Brute-forcing passwords

 Credential stuffing

 Brute-forcing logins

 Testing session management mechanisms

 Analyzing session token generation

 Decoding opaque data

 Identifying which parts of a token impact the response

 Determining the session timeout

 Generating a CSRF proof-of-concept

 Working with JWTs

 Maintaining an authenticated session

 Testing access controls

 Testing for privilege escalation

 Testing horizontal access controls

 Testing for IDORs

 Testing for parameter-based access control

 Spoofing your IP address using Burp Proxy match and replace

 Testing input validation

 Bypassing client-side controls

 SQL injection

 Testing for SQL injection vulnerabilities

 Cross-site scripting (XSS)

 Identifying reflected input

 Testing for DOM XSS with DOM Invader

 Testing for web message DOM XSS with DOM Invader

 Testing for reflected XSS manually

 Testing for stored XSS

 Bypassing XSS filters by enumerating permitted tags and attributes

 Testing for blind XSS

 Client-side prototype pollution

 OS command injection

 Testing for OS command injection vulnerabilities

 Testing for asynchronous OS command injection vulnerabilities

 Exploiting OS command injection vulnerabilities to exfiltrate data

 XXE injection

 Testing for XXE injection vulnerabilities

 Testing for blind XXE injection vulnerabilities

 Testing for directory traversal vulnerabilities

 Testing for clickjacking

 Testing for SSRF vulnerabilities

 Testing for SSRF

 Testing for blind SSRF

 Testing for WebSocket vulnerabilities

 Manipulating WebSocket messages

 Manipulating WebSocket handshakes

 Working with GraphQL in Burp Suite

 Complementing your manual testing with Burp Scanner

 Tools

 Dashboard

 Burp's browser

 Proxy

 Getting started with Burp Proxy

 Proxy intercept

 HTTP history

 Filtering HTTP history

 Filtering with scripts

 Adding custom columns

 WebSockets history

 Filtering WebSockets history

 Filtering with scripts

 Adding custom columns

 Match and replace rules

 Creating rules

 Creating rules with scripts

 Testing rules

 Settings

 Managing CA certificates

 Invisible proxying

 Repeater

 Getting started

 Working with HTTP messages

 Using Burp AI in Repeater

 Generating AI-powered explanations

 Automating tasks with custom actions

 Creating custom actions

 Loading custom actions

 Running custom actions

 Managing custom actions

 Sending grouped HTTP requests

 Working with WebSocket messages

 Managing tabs

 Managing tab groups

 Settings

 Tab-specific settings

 Intruder

 Getting started

 Configuring attacks

 Payload positions

 Attack types

 Payload types

 Payload lists

 Payload processing

 Resource pools

 Attack settings

 Managing tabs

 Attack results

 Editing attacks

 Saving attacks

 Viewing results

 Analyzing results

 Filtering results

 Testing workflow

 Typical uses

 Enumerating identifiers

 Fuzzing

 Harvesting data

 Enumerating subdomains

 Target

 Site map

 Getting started

 Workflow tools

 Filtering the site map

 Filtering the site map with scripts

 Comparing site maps

 Comparison results

 Editing the layout

 Scope

 Crawl paths

 Issue definitions

 Manual application mapping

 Reviewing unrequested items

 Analyzing the attack surface

 Inspector

 Getting started

 Modifying requests

 Settings

 Message editor

 Text editor

 Settings

 Collaborator [Pro only]

 Getting started

 Settings

 Logger

 Getting started

 Working with Logger entries

 Adding custom columns

 Filtering Logger

 Capture filter

 Capture filter with scripts

 View filter

 View filter with scripts

 Task Logger

 Viewing requests sent by Burp extensions

 Sequencer

 Getting started

 Obtaining a token sample

 Live capture

 Settings

 Results

 Tests

 DOM Invader

 Enabling DOM Invader

 Testing for DOM XSS

 Testing with web messages

 Testing for prototype pollution

 Testing for DOM clobbering

 Settings

 Main settings

 Attack types

 Web message settings

 Prototype pollution settings

 Misc settings

 Canary settings

 Clickbandit

 Comparer

 Settings

 Decoder

 Engagement tools

 Target analyzer

 Content discovery

 Generate CSRF PoC

 Manual testing simulator

 Infiltrator

 Organizer

 Annotating Organizer items

 Filtering Burp Organizer

 Collections

 Command palette

 Search

 Context menu

 Filter settings

 Extending Burp

 Bambdas

 Managing scripts

 Importing scripts

 Creating scripts

 Writing custom actions

 Worked example

 Writing guide

 Developing AI features

 Best practices for writing AI features

 Submitting scripts to GitHub

 Troubleshooting

 API JavaDoc

 GitHub repo

 Custom scan checks

 Managing custom scan checks

 Importing custom scan checks

 Creating custom scan checks

Writing guide 

Passive worked example 

Active worked example 

 Testing custom scan checks

 BCheck definitions

 Submitting BChecks to GitHub

 Submitting scripts to GitHub

 Extensions

 Installing extensions

 Installing from the BApp Store

 Installing manually

 Managing extensions

 Using AI extensions

 Troubleshooting extensions

 Viewing requests sent by extensions

 Creating extensions

 Setting up your development environment

 Using the starter project

 Manual setup

 Writing your first extension

 Extension tutorials

 Adding a settings panel

 Adding a hotkey

 Setting up remote debugging

 Using a remote debugger

 Loading your extension in Burp

 BApp Store acceptance criteria

 Submitting extensions to the BApp Store

 Maintaining extensions on the BApp Store

 Creating AI extensions

 Best practices for writing AI extensions

 Developing AI features in extensions

 Montoya API 

 JavaDoc

 GitHub

 Example extensions

 Extender API (Legacy) 

 JavaDoc

 Examples

 Running scans [Pro only]

 Scanning web applications

 Running a full crawl and audit

 Scanning specific HTTP messages

 Configuring scans

 Setting scan scope

 Configuring application logins

 Adding usernames and passwords

 Adding recorded login sequences

 Managing application logins using the configuration library

 Managing resource pools for scans

 Running API-only scans

 Configuring authentication

 Configuring scans

 Managing resource pools for scans

 Adding custom scan checks

 Adding extension scan checks

 Live tasks

 Creating live tasks

 Task execution settings

 Viewing scan and live task results

 Summary

 Audit items

 Insertion points

 Issues

 Event log

 Audit log

 Live crawl view

 Exploring issues with AI

 Reporting scan results

 Generating a report

 Report settings

 Burp Scanner Sample Report

 AI features (Burp AI)

 AI credits

 AI trust and data handling

 Troubleshooting AI connectivity

 Prompting best practices for Burp AI in Repeater

 Burp AT

 Getting started with Burp AT

 Tasks

 Prompting Burp AT effectively

 Tools

 Skills

 Configuring autonomy

 Working with Burp AT's results

 Project files

 Creating project files

 Managing project files

 Settings

 Key settings

 Tool settings

 Proxy

 Intruder

 Repeater

 Comparer

 Sequencer

 Burp's browser

 Project settings

 Scope

 Collaborator

 Tasks

 Automatic backup

 Logging

 Session settings

 Sessions

 Session handling rule editor

 Macro editor

 Network settings

 Connections

 DNS

 TLS

 HTTP

 User interface settings

 Side panel

 Message editor

 Hotkeys

 Display

 Suite settings

 REST API

 Updates

 Becoming an early adopter

 Performance

 Temporary files location

 Startup behavior

 Shutdown behavior

 AI

 Extensions

 Configuration library

 Response extraction rules

 Customizing Burp's layout

 Customizing top-level tabs

 Customizing tables

 Testing mobile applications

 Configuring iOS devices

 Configuring Android devices

 Troubleshooting

 Testing with HTTP/2

 HTTP/2 basics

 HTTP/2 in the message editor

 Performing HTTP/2 exclusive attacks

 Training

 Troubleshooting

 Common errors

 Performance issues

 Launching from the command line

 Setting Java options

Support Center 
Documentation 
Desktop editions 
Getting started 

 Professional Community Edition 

## Getting started with Burp Suite

 Last updated: 
 August 27, 2026 

 Read time: 
 1 Minute 

 Burp Suite is a comprehensive suite of tools for web application security testing.

 This interactive tutorial is designed to get you started with the core features of Burp Suite as quickly as possible. It uses deliberately vulnerable labs from the Web Security Academy to give you practical experience of how Burp Suite works.

 First step - Downloading and installing Burp Suite 
 CONTINUE

## In this tutorial

Downloading and installing Burp Suite. 

Intercepting HTTP traffic with Burp Proxy. 

Modifying requests in Burp Proxy. 

Setting the target scope. 

Manually reissuing requests with Burp Repeater. 

Running your first scan. 

What next? 

Burp Suite 
 Web vulnerability scanner
 Burp Suite Editions
 Release Notes

Vulnerabilities 
 Cross-site scripting (XSS)
 SQL injection
 Cross-site request forgery
 XML external entity injection
 Directory traversal
 Server-side request forgery

Customers 
 Organizations
 Testers
 Developers

Company 
 About
 Careers
 Contact
 Legal
 Privacy Notice
 Modern Slavery Statement

Insights 
 Web Security Academy
 Blog
 Research

 Follow us

© 2026 PortSwigger Ltd.
