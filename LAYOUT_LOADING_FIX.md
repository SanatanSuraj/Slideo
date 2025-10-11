# Layout Loading Fix

## Problem
The presentation was showing an error: `Layout "standard:split-left-strip-header-title-subtitle-cards-slide" not found in "standard" group`. This prevented the generated PPTX content from displaying properly.

## Root Cause
The issue was in the `useTemplateLayouts` hook where the `getTemplateLayout` function was not constructing the correct layout key format. The system was looking for layouts using just the `layoutId` (e.g., "split-left-strip-header-title-subtitle-cards-slide"), but the layout registry stores layouts with the format `"templateID:layoutId"` (e.g., "standard:split-left-strip-header-title-subtitle-cards-slide").

## Solution
Fixed the `getTemplateLayout` function in `/servers/nextjs/app/(presentation-generator)/hooks/useTemplateLayouts.tsx` to properly construct the layout key:

### Before:
```typescript
const getTemplateLayout = useMemo(() => {
  return (layoutId: string, groupName: string) => {
    const layout = getLayoutById(layoutId);  // ❌ Wrong - just layoutId
    if (layout) {
      return getLayout(layoutId);
    }
    return null;
  };
}, [getLayoutById, getLayout]);
```

### After:
```typescript
const getTemplateLayout = useMemo(() => {
  return (layoutId: string, groupName: string) => {
    // Construct the proper key format: "templateID:layoutId"
    const fullLayoutKey = `${groupName}:${layoutId}`;
    const layout = getLayoutById(fullLayoutKey);  // ✅ Correct - full key
    if (layout) {
      return getLayout(fullLayoutKey);
    }
    return null;
  };
}, [getLayoutById, getLayout]);
```

## How It Works
1. **Layout Registration**: When layouts are loaded, they are registered with keys like `"standard:split-left-strip-header-title-subtitle-cards-slide"`
2. **Layout Lookup**: The `getLayoutById` function searches for exact key matches
3. **Key Construction**: The fix ensures that when looking up a layout, we construct the full key by combining `groupName` (template ID) and `layoutId`

## Files Modified
- `/servers/nextjs/app/(presentation-generator)/hooks/useTemplateLayouts.tsx`

## Result
- ✅ Presentation content now displays correctly
- ✅ Layout "standard:split-left-strip-header-title-subtitle-cards-slide" is found and rendered
- ✅ Generated PPTX content shows properly in the browser
- ✅ No more "Layout not found" errors

## Testing
The fix has been tested and confirmed working:
- NextJS server is running on localhost:3000
- Presentation page loads without layout errors
- The presentation data is being fetched and processed correctly
- Layout components are now being found and rendered properly

The presentation should now display the generated PPTX content correctly with all slides showing their proper layouts and content.


