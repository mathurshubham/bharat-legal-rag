---
source_url: https://help.clickup.com/hc/en-us/articles/6303528232855
source_site: clickup
scraped_at_iso: 2026-06-26T11:12:09Z
---

[Skip to main content](https://help.clickup.com/hc/en-us/articles/6303528232855#page-container)

Categories


# oops

## The page you were looking for doesn't exist

You may have mistyped the address or the page may have moved


[Take me back to the home page](https://help.clickup.com/hc/en-us "Home")




 <% var getColumnClasses = function(columnNumber) {
 var classNames = numberColumns === 'auto' ? 'col-auto' : 'col-12';
 if (numberColumns >= 2) classNames += ' md:col-6';
 if (numberColumns >= 3) classNames += ' lg:col-4';
 if (numberColumns >= 4) classNames += ' xl:col-3';
 return classNames;
 } %>


<% blocks.forEach(function(block, index) { %>
 - [<% if (imageHeight) { %>\\
![](https://help.clickup.com/hc/en-us/articles/6303528232855)\\
<% } %>\\
<% if (block.name) { %>\\
**<%= block.name %>**\\
<% } %>\\
<% if (block.description) { %>\\
\\
\\
<%= block.description %>\\
\\
\\
<% } %>](https://help.clickup.com/hc/en-us/articles/6303528232855)


<% }) %>


## Can't find what you're looking for?

[Contact Us](https://help.clickup.com/hc/en-us/articles/6303528232855)

### Categories

<% categories.forEach(function(category, index) { %>
 - [<%= category.name %>](https://help.clickup.com/hc/en-us/articles/6303528232855)



<%= partial('partial-article-list-sections', {
id: 'category-' + category.id,
parentId: '#sidebar-navigation',
sections: category.sections,
activeCategoryId: activeCategoryId,
activeSectionId: activeSectionId,
activeArticleId: activeArticleId,
partial: partial
}) %>



<% }); %>


 <% var maxSections = 12 %>


### Toggle navigation menu

<% categories.forEach(function(category, index) { %>
 - ### [<%= category.name %>](https://help.clickup.com/hc/en-us/articles/6303528232855)


<%= partial('partial-section-list-sections', { parent: category, sections: category.sections, maxSections: maxSections, partial: partial }) %>


<% }); %>


### Categories

### [Categories](https://help.clickup.com/hc/en-us/articles/6303528232855)

<% categories.forEach(function(category) { %>
 - [<%= category.name %>](https://help.clickup.com/hc/en-us/articles/6303528232855)

<% }); %>


 <% if (sections.length) { %>


 <% sections.forEach(function(section) { %>
 - [<%= section.name %>](https://help.clickup.com/hc/en-us/articles/6303528232855)



   <%= partial('partial-article-list-sections', {
   id: 'section-' + section.id,
   parentId: '#' + id,
   sections: section.sections,
   activeCategoryId: activeCategoryId,
   activeSectionId: activeSectionId,
   activeArticleId: activeArticleId,
   partial: partial
   }) %>


   <% if (section.articles.length) { %>

   <% section.articles.forEach(function(article) { %>
   - [<%= article.title %>](https://help.clickup.com/hc/en-us/articles/6303528232855)

 <% }); %>
 <% } %>



 <% }); %>


 <% } %>

 <% if (sections.length) { %>


 <% sections.slice(0, maxSections).forEach(function(section) { %>
 - [<%= section.name %>](https://help.clickup.com/hc/en-us/articles/6303528232855)
   <%= partial('partial-section-list-sections', { parent: section, sections: section.sections, maxSections: maxSections, partial: partial }) %>


 <% }); %>
 <% if (sections.length > maxSections) { %>
 - [See more](https://help.clickup.com/hc/en-us/articles/6303528232855)

 <% } %>


 <% } %>





 <% if (forms.length) { %>
 <% if (title) { %>

 <% } %>




**Platform Support**
Getting Started, ClickUp Features, Integrations, Use Case Support

**Billing**
Payments, Invoices, Pricing, Seats, Changing Your Plan

**My Account**
Logging In, SSO, Account Settings, Security  Privacy

[**Technical Support** \\
Bug Reports, Error Codes, ClickUp API](https://help.clickup.com/hc/en-us/articles/6303528232855)

[**Marketing** \\
Blog Posts, Sponsorship Requests, Press Inquiries](https://help.clickup.com/hc/en-us/articles/6303528232855)

[**Sales & Solutions** \\
Connect with the ClickUp Sales or Solutions Teams](https://help.clickup.com/hc/en-us/articles/6303528232855)

<% } %>

## Can't find what you're looking for?



Contact Us




## Can't find what you're looking for?



Contact Us




[**Templates ![](https://help.clickup.com/hc/en-us/articles/6303528232855)** \\
Find ready to use templates](https://clickup.com/templates)

[**ClickUp University ![](https://help.clickup.com/hc/en-us/articles/6303528232855)** \\
Earn certifications to level up your skills](https://university.clickup.com/)

**Contact us**
Connect with our support team

[**YouTube videos ![](https://help.clickup.com/hc/en-us/articles/6303528232855)** \\
Stay up to date with the latest features](https://www.youtube.com/@ClickUpProductivity)

[**Join our communities ![](https://help.clickup.com/hc/en-us/articles/6303528232855)** \\
Join one of our global communities](https://clickup.com/community)

[**Request a feature ![](https://help.clickup.com/hc/en-us/articles/6303528232855)** \\
Suggest and vote on new features](https://clickup.canny.io/)

Get Help

Support Chat