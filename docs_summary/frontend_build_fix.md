# Frontend Build Fix

This document explains how to fix the frontend build issue with Tailwind CSS.

## Issue

When trying to build the frontend, you may encounter an error like this:

```
[vite:css] [postcss] Cannot apply unknown utility class: bg-tertiary
```

This happens because the `bg-tertiary` utility class is defined in the Tailwind configuration, but there's a conflict with the HeroUI theme.

## Solution

There are two ways to fix this issue:

### Option 1: Add the tertiary color to the dark theme

Edit the `tailwind.config.js` file and add the tertiary color to the dark theme:

```javascript
themes: {
  dark: {
    colors: {
      primary: "#4465DB",
      logo: "#CFB755",
      tertiary: "#454545", // Add this line
    },
  },
},
```

### Option 2: Use direct CSS instead of utility classes

Edit the `src/tailwind.css` file and replace the utility class with direct CSS:

```css
.button-base {
  background-color: #454545;
  border: 1px solid #666;
  border-radius: 0.25rem;
}
```

## Running the Web Server

After fixing the frontend build issue, you can run the web server with:

```bash
python start_web_server.py
```

This will start the Vortex AI web server on http://0.0.0.0:12000.