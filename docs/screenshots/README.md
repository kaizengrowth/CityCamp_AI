# 📸 Application Screenshots

This directory contains screenshots of the CityCamp AI application showcasing various features and user interfaces.

## 📁 Screenshot Organization

```
docs/screenshots/
├── homepage/
│   ├── landing-page.png          # Main landing page
│   ├── dashboard-overview.png    # User dashboard
│   └── navigation-menu.png       # Main navigation
│
├── meetings/
│   ├── meeting-list.png          # Categorized meeting list
│   ├── meeting-details.png       # Individual meeting details
│   ├── search-filters.png        # Search and filter interface
│   └── ai-categorization.png     # AI topic categorization
│
├── chatbot/
│   ├── chatbot-interface.png     # Main chatbot UI
│   ├── query-examples.png        # Sample queries and responses
│   └── meeting-summary.png       # AI-generated summaries
│
├── notifications/
│   ├── signup-form.png           # Notification preferences
│   ├── email-generation.png      # AI email composer
│   └── sms-interface.png         # SMS notification setup
│
├── admin/
│   ├── data-import.png           # Meeting data import
│   ├── analytics-dashboard.png   # Usage analytics
│   └── ai-processing.png         # AI categorization results
│
└── README.md                     # This file
```

## 📋 Screenshot Guidelines

### **Taking Screenshots**
1. **Resolution**: Use 1920x1080 or higher for desktop views
2. **Mobile**: Include both mobile (375x667) and tablet (768x1024) views
3. **Browser**: Use latest Chrome/Safari with clean UI (no extensions visible)
4. **Data**: Use realistic sample data, not Lorem ipsum
5. **Privacy**: Ensure no real personal information is visible

### **File Naming Convention**
- Use kebab-case: `feature-name-description.png`
- Include viewport: `meeting-list-desktop.png`, `meeting-list-mobile.png`
- Version control: `dashboard-v2.png` for major UI updates

### **Image Requirements**
- **Format**: PNG for UI screenshots (better quality)
- **Size**: Optimize for web (< 500KB per image)
- **Quality**: High quality but web-optimized
- **Annotations**: Add callouts/highlights for key features when needed

## 🛠️ Screenshot Management

### **Automated Screenshot Capture**
```bash
# Install playwright for automated screenshots
npm install -g playwright

# Capture screenshots (when implemented)
npm run screenshots:capture

# Optimize images
npm run screenshots:optimize
```

### **Manual Screenshot Updates**
1. **Navigate** to the live application: https://d1s9nkkr0t3pmn.cloudfront.net
2. **Capture** screenshots according to the guidelines above
3. **Save** in appropriate subdirectory with descriptive filename
4. **Optimize** images for web using tools like:
   - ImageOptim (Mac)
   - TinyPNG (Web)
   - `npm run optimize-images` (if available)

### **Integration with README**
Update the main README.md when adding new screenshots:

```markdown
### **📅 Meeting Analytics & Search**
![Meeting List](docs/screenshots/meetings/meeting-list-desktop.png)
*AI-categorized meetings with smart filtering*

![Meeting Details](docs/screenshots/meetings/meeting-details-desktop.png)
*Detailed meeting view with agenda extraction*
```

## 🔄 Update Schedule

- **Major Feature Releases**: Update all relevant screenshots
- **UI Changes**: Update affected screenshots within 1 week
- **Quarterly Review**: Audit all screenshots for accuracy
- **Version Tags**: Tag screenshots with release versions

## 📊 Current Screenshot Status

| Feature Area | Desktop | Mobile | Last Updated | Status |
|--------------|---------|--------|--------------|--------|
| Homepage | ❌ | ❌ | N/A | Needed |
| Meeting List | ❌ | ❌ | N/A | Needed |
| Meeting Details | ❌ | ❌ | N/A | Needed |
| Chatbot Interface | ❌ | ❌ | N/A | Needed |
| Notifications | ❌ | ❌ | N/A | Needed |
| Admin Dashboard | ❌ | ❌ | N/A | Needed |

## 🎯 Priority Screenshots Needed

1. **Homepage Landing Page** - Shows value proposition and main CTA
2. **Meeting List with Filters** - Demonstrates AI categorization
3. **Meeting Details View** - Shows agenda extraction and analysis
4. **Chatbot Interaction** - AI assistant responding to queries
5. **Notification Signup** - User preference interface

## 📝 Notes

- Screenshots should represent the current production version
- Include dark/light mode variants if applicable
- Consider internationalization if multiple languages supported
- Maintain consistent browser chrome and viewport sizes
- Update screenshots before major releases or demos

---

**Need to add screenshots?** Follow the guidelines above or run the automated capture scripts when available!
