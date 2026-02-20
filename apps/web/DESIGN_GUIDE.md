# ZETA Platform Design System
## Google Drive Light Theme Implementation

This design system matches Google Drive's clean, professional aesthetic with precise color matching, typography, and component styling.

---

## 🎨 Color Palette

### Primary Colors
```css
--gdrive-bg: #F8F9FA        /* Main background (very light gray) */
--gdrive-white: #FFFFFF      /* Cards, sidebar, content areas */
--gdrive-blue: #1A73E8       /* Primary action color (Google Blue) */
--gdrive-blue-hover: #1765CC /* Darker blue on hover */
--gdrive-blue-active: #1557B0 /* Even darker on active */
```

### Interactive States
```css
--gdrive-hover: #E8F0FE      /* Light blue for active/selected items */
--gdrive-gray-hover: #F1F3F4 /* Gray hover background */
```

### Text & Borders
```css
--gdrive-text: #202124       /* Primary text (dark gray) */
--gdrive-secondary: #5F6368  /* Secondary text (gray) */
--gdrive-border: #DADCE0     /* Borders and dividers */
```

### Status Colors
```css
--gdrive-success: #1E8E3E    /* Success/Active green */
--gdrive-success-bg: #E6F4EA /* Success background */
--gdrive-danger: #D93025     /* Error/Danger red */
--gdrive-danger-bg: #FCE8E6  /* Danger background */
--gdrive-warning: #E37400    /* Warning orange */
--gdrive-warning-bg: #FEF7E0 /* Warning background */
```

---

## 📐 Typography

### Font Family
```css
font-family: 'Google Sans', 'Roboto', -apple-system, sans-serif;
```

### Font Sizes
```css
11px - Extra small (labels, captions)
13px - Small (secondary text, metadata)
14px - Base (body text, default)
16px - Large (subheadings)
18px - XL (card titles)
22px - 2XL (section headings)
28px - 3XL (page titles)
```

### Font Weights
```css
400 - Regular (body text)
500 - Medium (buttons, headings, emphasis)
700 - Bold (only when strong emphasis needed)
```

---

## 🔲 Shadows

Google Drive uses subtle, layered shadows:

```css
/* Small - Cards at rest */
shadow-google-sm: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);

/* Medium - Cards on hover, modals */
shadow-google-md: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);

/* Large - Dropdowns, popovers */
shadow-google-lg: 0 2px 6px 2px rgba(60,64,67,0.15), 0 8px 24px 4px rgba(60,64,67,0.15);
```

---

## 📦 Border Radius

```css
4px  - Buttons, small elements (rounded-google-sm)
8px  - Cards, inputs, containers (rounded-google)
50%  - Avatars, status dots (rounded-full)
```

---

## 🧩 Components

### 1. Card

**Usage:** Content containers, information groups

```tsx
<Card hover>
  <div className="flex items-center gap-4">
    <div className="p-3 bg-gdrive-hover rounded-google">
      <Icon size={28} className="text-gdrive-blue" />
    </div>
    <div>
      <p className="text-xs text-gdrive-secondary uppercase">Label</p>
      <p className="text-3xl font-medium text-gdrive-text">Value</p>
    </div>
  </div>
</Card>
```

**Styles:**
- Background: `bg-gdrive-white`
- Border: `border border-gdrive-border`
- Shadow: `shadow-google-sm`
- Hover: `hover:shadow-google-md` (when interactive)
- Padding: `p-6`
- Border radius: `rounded-google` (8px)

---

### 2. Button

**Variants:**

**Primary** (Main actions)
```tsx
<Button variant="primary">Save Changes</Button>
```
- Background: `bg-gdrive-blue`
- Hover: `hover:bg-gdrive-blue-hover`
- Text: `text-white`
- Shadow: `shadow-google-sm`

**Secondary** (Alternative actions)
```tsx
<Button variant="secondary">Cancel</Button>
```
- Background: `bg-gdrive-white`
- Border: `border-gdrive-border`
- Hover: `hover:bg-gdrive-gray-hover`
- Text: `text-gdrive-text`

**Text** (Tertiary actions)
```tsx
<Button variant="text">Learn More</Button>
```
- No background
- Hover: `hover:bg-gdrive-gray-hover`
- Text: `text-gdrive-secondary`

**Danger** (Destructive actions)
```tsx
<Button variant="danger">Delete</Button>
```
- Background: `bg-gdrive-danger`
- Hover: `hover:bg-[#C5221F]`
- Text: `text-white`

---

### 3. Input Fields

```tsx
<Input 
  label="Email Address"
  placeholder="Enter your email"
  error={errors.email}
/>
```

**Styles:**
- Background: `bg-gdrive-white`
- Border: `border-gdrive-border`
- Hover: `hover:border-gdrive-secondary`
- Focus: `focus:border-gdrive-blue focus:ring-2 focus:ring-gdrive-hover`
- Border radius: `rounded-google-sm` (4px)
- Padding: `px-4 py-2.5`

---

### 4. Table

**Usage:** Data lists with hover states

```tsx
<Table>
  <Table.Header>
    <Table.Row>
      <Table.Head sortable>Name</Table.Head>
      <Table.Head>Status</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    <Table.Row selected={isSelected}>
      <Table.Cell>Product Name</Table.Cell>
      <Table.Cell>Active</Table.Cell>
    </Table.Row>
  </Table.Body>
</Table>
```

**Styles:**
- No outer borders
- Only bottom borders on rows: `border-b border-gdrive-border`
- Row hover: `hover:bg-gdrive-gray-hover`
- Selected row: `bg-gdrive-hover`
- Header text: `text-xs uppercase text-gdrive-secondary`

---

### 5. Sidebar Navigation

**Active item:**
```tsx
className="bg-gdrive-hover text-gdrive-blue font-medium"
```

**Inactive item:**
```tsx
className="text-gdrive-text hover:bg-gdrive-gray-hover"
```

**Icon styling:**
- Active: `text-gdrive-blue`
- Inactive: `text-gdrive-secondary group-hover:text-gdrive-text`
- Size: `20px`
- Stroke width: `2`

---

### 6. Status Badges

**Active/Success:**
```tsx
<span className="flex items-center gap-2 text-gdrive-success">
  <span className="w-2 h-2 rounded-full bg-gdrive-success"></span>
  Active
</span>
```

**Inactive/Error:**
```tsx
<span className="flex items-center gap-2 text-gdrive-danger">
  <span className="w-2 h-2 rounded-full bg-gdrive-danger"></span>
  Inactive
</span>
```

**Warning:**
```tsx
<span className="flex items-center gap-2 text-gdrive-warning">
  <span className="w-2 h-2 rounded-full bg-gdrive-warning"></span>
  Pending
</span>
```

---

### 7. Search Bar

Google Drive's signature search style:

```tsx
<div className="relative">
  <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gdrive-secondary" size={20} />
  <input
    type="text"
    placeholder="Search in ZETA Platform"
    className="
      w-full bg-gdrive-bg text-gdrive-text 
      pl-12 pr-4 py-2.5 rounded-google
      border-0 
      focus:bg-gdrive-white focus:shadow-google-md 
      transition-all duration-200
    "
  />
</div>
```

---

## 🎯 Usage Guidelines

### DO:
✅ Use Google Sans or Roboto fonts  
✅ Keep shadows subtle and layered  
✅ Use the exact Google blue (#1A73E8) for primary actions  
✅ Apply 8px border radius to cards  
✅ Use 4px border radius for buttons  
✅ Keep backgrounds clean (white or light gray)  
✅ Use status dots with text labels  
✅ Add hover states to interactive elements  
✅ Use proper font sizes (14px for body, 28px for titles)  

### DON'T:
❌ Use emoji in production UI  
❌ Use bright or neon colors  
❌ Add heavy shadows or glows  
❌ Use gradients  
❌ Use black (#000000) backgrounds  
❌ Mix multiple primary colors  
❌ Use icons without proper spacing  
❌ Forget hover states on clickable items  

---

## 📱 Responsive Design

### Breakpoints
```css
sm: 640px   - Mobile
md: 768px   - Tablet
lg: 1024px  - Desktop
xl: 1280px  - Large desktop
```

### Grid Layouts
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Cards */}
</div>
```

---

## ♿ Accessibility

### Focus States
All interactive elements must have visible focus indicators:
```css
focus:outline-none focus:border-gdrive-blue focus:ring-2 focus:ring-gdrive-hover
```

### Color Contrast
All text meets WCAG AA standards:
- Primary text (#202124) on white: 16.03:1 ✅
- Secondary text (#5F6368) on white: 7.49:1 ✅
- Blue text (#1A73E8) on white: 4.56:1 ✅

### Keyboard Navigation
- Tab order follows logical flow
- All actions accessible via keyboard
- Visible focus indicators

---

## 🔧 Implementation

### Tailwind Config
```typescript
// tailwind.config.ts
colors: {
  'gdrive-bg': '#F8F9FA',
  'gdrive-white': '#FFFFFF',
  'gdrive-blue': '#1A73E8',
  // ... rest of palette
}
```

### CSS Variables
```css
/* globals.css */
:root {
  --gdrive-bg: #F8F9FA;
  --gdrive-blue: #1A73E8;
  /* ... rest of variables */
}
```

---

## 📚 Examples

### Dashboard Card
```tsx
<Card hover>
  <div className="flex items-center gap-4">
    <div className="p-3 bg-gdrive-hover rounded-google">
      <Building2 size={28} className="text-gdrive-blue" strokeWidth={2} />
    </div>
    <div>
      <p className="text-xs text-gdrive-secondary uppercase tracking-wide">
        Total Cities
      </p>
      <p className="text-3xl font-medium text-gdrive-text mt-1">
        24
      </p>
    </div>
  </div>
</Card>
```

### Form Layout
```tsx
<Card>
  <h2 className="text-xl font-medium text-gdrive-text mb-6">
    Account Settings
  </h2>
  <div className="space-y-4">
    <Input label="Full Name" placeholder="John Doe" />
    <Input label="Email" type="email" placeholder="john@example.com" />
    <div className="flex gap-3 mt-6">
      <Button variant="primary">Save Changes</Button>
      <Button variant="secondary">Cancel</Button>
    </div>
  </div>
</Card>
```

---

## 🔄 Updates & Maintenance

This design system should be updated when:
- Google Drive updates their design language
- New components are needed
- Accessibility standards change
- User feedback suggests improvements

**Last Updated:** February 20, 2026  
**Version:** 2.0  
**Based on:** Google Drive (2026)
