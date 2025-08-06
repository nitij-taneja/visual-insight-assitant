# UI/UX Design Specifications - Visual Insight Assistant

## 1. Design System Foundation

### 1.1 Color System

**Primary Palette**
- Primary Blue: #2563EB - Used for primary actions, links, and key interactive elements
- Primary Blue Light: #3B82F6 - Hover states and secondary emphasis
- Primary Blue Dark: #1D4ED8 - Active states and high contrast needs

**Secondary Palette**
- Intelligent Purple: #7C3AED - AI-related features, insights, and smart recommendations
- Purple Light: #8B5CF6 - Subtle AI indicators and secondary purple elements
- Purple Dark: #6D28D9 - Active AI processing states

**Semantic Colors**
- Success Green: #059669 - Successful operations, completed analysis, positive insights
- Warning Orange: #D97706 - Attention-needed items, processing states, caution alerts
- Error Red: #DC2626 - Errors, violations, critical alerts, failed operations
- Info Cyan: #0891B2 - Informational messages, tips, neutral notifications

**Neutral Palette**
- Gray 900: #111827 - Primary text, headings
- Gray 700: #374151 - Secondary text, subheadings
- Gray 500: #6B7280 - Tertiary text, placeholders
- Gray 300: #D1D5DB - Borders, dividers
- Gray 100: #F3F4F6 - Background surfaces
- Gray 50: #F9FAFB - Page background, subtle surfaces

### 1.2 Typography System

**Font Families**
- Primary: 'Inter', system-ui, -apple-system, sans-serif
- Monospace: 'JetBrains Mono', 'Fira Code', monospace
- Display: 'Inter Display', 'Inter', sans-serif (for large headings)

**Type Scale**
- Display Large: 48px / 56px (3rem / 3.5rem)
- Display Medium: 36px / 44px (2.25rem / 2.75rem)
- Heading 1: 32px / 40px (2rem / 2.5rem)
- Heading 2: 24px / 32px (1.5rem / 2rem)
- Heading 3: 20px / 28px (1.25rem / 1.75rem)
- Body Large: 18px / 28px (1.125rem / 1.75rem)
- Body: 16px / 24px (1rem / 1.5rem)
- Body Small: 14px / 20px (0.875rem / 1.25rem)
- Caption: 12px / 16px (0.75rem / 1rem)

**Font Weights**
- Light: 300 - Subtle text, large displays
- Regular: 400 - Body text, standard content
- Medium: 500 - Emphasized text, labels
- Semibold: 600 - Headings, important text
- Bold: 700 - Strong emphasis, key information

### 1.3 Spacing System

**Base Unit: 4px**
- xs: 4px (0.25rem)
- sm: 8px (0.5rem)
- md: 12px (0.75rem)
- lg: 16px (1rem)
- xl: 20px (1.25rem)
- 2xl: 24px (1.5rem)
- 3xl: 32px (2rem)
- 4xl: 40px (2.5rem)
- 5xl: 48px (3rem)
- 6xl: 64px (4rem)

### 1.4 Border Radius System

- None: 0px
- Small: 4px - Buttons, form elements
- Medium: 8px - Cards, panels
- Large: 12px - Modals, major containers
- XL: 16px - Hero sections, feature cards
- Full: 9999px - Pills, circular elements

### 1.5 Shadow System

**Elevation Levels**
- Level 1: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)
- Level 2: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)
- Level 3: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)
- Level 4: 0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)

## 2. Component Specifications

### 2.1 Navigation Header

**Structure**
- Height: 64px (4rem)
- Background: White with subtle shadow (Level 1)
- Logo placement: Left side, 32px from edge
- Navigation items: Center-aligned horizontal menu
- User actions: Right side (profile, notifications, settings)

**Interactive States**
- Default: Gray 700 text
- Hover: Primary blue text with smooth transition (200ms)
- Active: Primary blue text with underline indicator
- Focus: Blue outline with 2px border radius

### 2.2 Video Player Component

**Dimensions**
- Aspect ratio: 16:9 (responsive)
- Minimum width: 320px
- Maximum width: 1200px
- Border radius: 12px

**Controls**
- Play/pause button: 48px circular button with primary blue background
- Timeline scrubber: Custom styled with event markers
- Volume control: Horizontal slider with mute toggle
- Fullscreen toggle: Icon button in top-right corner

**Event Overlays**
- Event markers: Colored dots on timeline (green=normal, orange=warning, red=violation)
- Bounding boxes: Semi-transparent colored rectangles over detected objects
- Timestamp labels: Small badges with white text on semi-transparent background

### 2.3 Chat Interface

**Message Container**
- Width: 100% with max-width 800px
- Padding: 24px
- Background: Gray 50
- Border radius: 12px

**Message Bubbles**
- User messages: Right-aligned, primary blue background, white text
- AI messages: Left-aligned, white background, gray 900 text
- Max width: 70% of container
- Border radius: 18px with tail indicator
- Padding: 12px 16px
- Shadow: Level 1 elevation

**Input Field**
- Height: 48px
- Border: 1px solid gray 300
- Border radius: 24px
- Padding: 12px 20px
- Focus state: Primary blue border with shadow
- Send button: Circular button with primary blue background

### 2.4 Analysis Dashboard

**Layout Grid**
- 12-column responsive grid system
- Gutter: 24px
- Breakpoints: sm(640px), md(768px), lg(1024px), xl(1280px)

**Insight Cards**
- Background: White
- Border radius: 12px
- Padding: 24px
- Shadow: Level 2 elevation
- Border: 1px solid gray 200

**Chart Components**
- Timeline chart: Line graph with event markers
- Activity heatmap: Color-coded grid showing activity intensity
- Event distribution: Donut chart with semantic colors
- Confidence meters: Progress bars with gradient fills

### 2.5 Modal Components

**Overlay**
- Background: rgba(0, 0, 0, 0.5)
- Backdrop blur: 4px
- Animation: Fade in/out (300ms ease)

**Modal Container**
- Background: White
- Border radius: 16px
- Max width: 600px
- Padding: 32px
- Shadow: Level 4 elevation
- Animation: Scale and fade (300ms ease)

## 3. Responsive Design Specifications

### 3.1 Breakpoint Strategy

**Mobile First Approach**
- Base styles: Mobile (320px+)
- Small: 640px+ (sm)
- Medium: 768px+ (md)
- Large: 1024px+ (lg)
- Extra Large: 1280px+ (xl)

### 3.2 Layout Adaptations

**Mobile (320px - 639px)**
- Single column layout
- Collapsible navigation menu
- Stacked video and chat interface
- Full-width components
- Touch-optimized button sizes (44px minimum)

**Tablet (640px - 1023px)**
- Two-column layout for main content
- Horizontal navigation bar
- Side-by-side video and chat
- Responsive grid system
- Hover states for supported devices

**Desktop (1024px+)**
- Multi-column dashboard layout
- Full navigation with all items visible
- Advanced interactions and hover effects
- Keyboard shortcuts support
- Multi-panel interface

### 3.3 Touch Interaction Guidelines

**Minimum Touch Targets**
- Buttons: 44px × 44px minimum
- Links: 32px × 32px minimum
- Form controls: 44px height minimum

**Gesture Support**
- Swipe: Navigate between video segments
- Pinch: Zoom video player
- Long press: Context menus and additional options
- Tap: Standard selection and activation

## 4. Animation and Interaction Design

### 4.1 Transition Specifications

**Duration Guidelines**
- Micro-interactions: 150ms - Button hovers, focus states
- Standard transitions: 300ms - Modal open/close, page transitions
- Complex animations: 500ms - Loading states, data visualizations

**Easing Functions**
- Ease-out: For entrances and user-initiated actions
- Ease-in: For exits and system-initiated actions
- Ease-in-out: For continuous movements and loops

### 4.2 Loading States

**Skeleton Screens**
- Animated placeholder content
- Matches final content structure
- Subtle shimmer effect (1.5s duration)
- Gray 200 base with gray 300 highlight

**Progress Indicators**
- Linear progress: For file uploads and processing
- Circular progress: For indeterminate loading
- Step indicators: For multi-stage processes

### 4.3 Feedback Animations

**Success States**
- Checkmark animation with scale and fade
- Green color transition
- Subtle bounce effect

**Error States**
- Shake animation for form validation
- Red color transition
- Error icon with attention-grabbing pulse

**Processing States**
- Pulsing animation for active processing
- Color cycling for AI analysis
- Smooth transitions between states

## 5. Accessibility Standards

### 5.1 WCAG 2.1 AA Compliance

**Color Contrast**
- Normal text: 4.5:1 minimum ratio
- Large text: 3:1 minimum ratio
- UI components: 3:1 minimum ratio
- Focus indicators: 3:1 minimum ratio

**Keyboard Navigation**
- Tab order: Logical and predictable
- Focus indicators: Visible and high contrast
- Skip links: Available for main content areas
- Keyboard shortcuts: Documented and accessible

### 5.2 Screen Reader Support

**Semantic HTML**
- Proper heading hierarchy (h1-h6)
- Landmark regions (header, main, aside, footer)
- Form labels and descriptions
- Button and link descriptions

**ARIA Attributes**
- aria-label: For icon buttons and complex controls
- aria-describedby: For additional context
- aria-live: For dynamic content updates
- role: For custom components

### 5.3 Motor Accessibility

**Large Touch Targets**
- Minimum 44px for touch interfaces
- Adequate spacing between interactive elements
- Alternative input methods support
- Reduced motion preferences respected

## 6. Performance Considerations

### 6.1 Optimization Strategies

**Image Optimization**
- WebP format with fallbacks
- Responsive image sizing
- Lazy loading for non-critical images
- Compression optimization

**Font Loading**
- Font display: swap for faster rendering
- Preload critical fonts
- Subset fonts for reduced file size
- System font fallbacks

### 6.2 Animation Performance

**Hardware Acceleration**
- Use transform and opacity for animations
- Avoid animating layout properties
- Use will-change sparingly
- Optimize for 60fps performance

This comprehensive design specification provides the foundation for creating a world-class user interface that is both beautiful and functional, ensuring an exceptional user experience across all devices and accessibility needs.

