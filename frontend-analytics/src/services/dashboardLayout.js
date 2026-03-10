// Custom Dashboard Layout Manager
import { useState, useCallback } from 'react'

export class DashboardLayoutManager {
  constructor(storageKey = 'dashboard-layouts') {
    this.storageKey = storageKey
    this.layouts = this.loadLayouts()
  }

  loadLayouts() {
    try {
      const saved = localStorage.getItem(this.storageKey)
      return saved ? JSON.parse(saved) : this.getDefaultLayouts()
    } catch (error) {
      console.error('Failed to load layouts:', error)
      return this.getDefaultLayouts()
    }
  }

  getDefaultLayouts() {
    return {
      default: {
        name: 'Default Layout',
        widgets: [
          { id: 'metrics-1', type: 'metric-cards', position: { x: 0, y: 0, w: 12, h: 2 } },
          { id: 'chart-1', type: 'line-chart', position: { x: 0, y: 2, w: 6, h: 3 } },
          { id: 'chart-2', type: 'bar-chart', position: { x: 6, y: 2, w: 6, h: 3 } },
          { id: 'table-1', type: 'data-table', position: { x: 0, y: 5, w: 12, h: 3 } }
        ]
      }
    }
  }

  createLayout(name, widgets = []) {
    const layoutId = `layout-${Date.now()}`
    this.layouts[layoutId] = {
      id: layoutId,
      name,
      widgets,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    this.saveLayouts()
    return this.layouts[layoutId]
  }

  updateLayout(layoutId, updates) {
    const layout = this.layouts[layoutId]
    if (!layout) return null

    Object.assign(layout, updates, {
      updatedAt: new Date().toISOString()
    })

    this.saveLayouts()
    return layout
  }

  addWidget(layoutId, widget) {
    const layout = this.layouts[layoutId]
    if (!layout) return null

    layout.widgets.push({
      id: `widget-${Date.now()}`,
      ...widget,
      addedAt: new Date().toISOString()
    })

    this.saveLayouts()
    return layout
  }

  removeWidget(layoutId, widgetId) {
    const layout = this.layouts[layoutId]
    if (!layout) return null

    layout.widgets = layout.widgets.filter(w => w.id !== widgetId)
    this.saveLayouts()
    return layout
  }

  updateWidgetPosition(layoutId, widgetId, position) {
    const layout = this.layouts[layoutId]
    if (!layout) return null

    const widget = layout.widgets.find(w => w.id === widgetId)
    if (widget) {
      widget.position = position
      this.saveLayouts()
    }

    return layout
  }

  reorderWidgets(layoutId, widgetIds) {
    const layout = this.layouts[layoutId]
    if (!layout) return null

    const widgetMap = new Map(layout.widgets.map(w => [w.id, w]))
    layout.widgets = widgetIds.map(id => widgetMap.get(id)).filter(Boolean)

    this.saveLayouts()
    return layout
  }

  deleteLayout(layoutId) {
    delete this.layouts[layoutId]
    this.saveLayouts()
  }

  getLayout(layoutId) {
    return this.layouts[layoutId]
  }

  getAllLayouts() {
    return Object.values(this.layouts)
  }

  duplicateLayout(layoutId, newName) {
    const original = this.layouts[layoutId]
    if (!original) return null

    const newLayout = {
      id: `layout-${Date.now()}`,
      name: newName || `${original.name} (Copy)`,
      widgets: JSON.parse(JSON.stringify(original.widgets)),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    this.layouts[newLayout.id] = newLayout
    this.saveLayouts()
    return newLayout
  }

  saveLayouts() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.layouts))
    } catch (error) {
      console.error('Failed to save layouts:', error)
    }
  }
}

// React Hook for Dashboard Layouts
export function useDashboardLayout(initialLayoutId = 'default') {
  const [currentLayoutId, setCurrentLayoutId] = useState(initialLayoutId)
  const [layoutManager] = useState(() => new DashboardLayoutManager())
  const [currentLayout, setCurrentLayout] = useState(
    layoutManager.getLayout(initialLayoutId)
  )

  const switchLayout = useCallback((layoutId) => {
    const layout = layoutManager.getLayout(layoutId)
    if (layout) {
      setCurrentLayoutId(layoutId)
      setCurrentLayout(layout)
    }
  }, [layoutManager])

  const updateLayout = useCallback((updates) => {
    const updated = layoutManager.updateLayout(currentLayoutId, updates)
    setCurrentLayout(updated)
  }, [layoutManager, currentLayoutId])

  const addWidget = useCallback((widget) => {
    const updated = layoutManager.addWidget(currentLayoutId, widget)
    setCurrentLayout(updated)
  }, [layoutManager, currentLayoutId])

  const removeWidget = useCallback((widgetId) => {
    const updated = layoutManager.removeWidget(currentLayoutId, widgetId)
    setCurrentLayout(updated)
  }, [layoutManager, currentLayoutId])

  const updateWidgetPosition = useCallback((widgetId, position) => {
    const updated = layoutManager.updateWidgetPosition(currentLayoutId, widgetId, position)
    setCurrentLayout(updated)
  }, [layoutManager, currentLayoutId])

  const createLayout = useCallback((name, widgets) => {
    const newLayout = layoutManager.createLayout(name, widgets)
    setCurrentLayoutId(newLayout.id)
    setCurrentLayout(newLayout)
    return newLayout
  }, [layoutManager])

  const deleteLayout = useCallback((layoutId) => {
    layoutManager.deleteLayout(layoutId)
    if (layoutId === currentLayoutId) {
      switchLayout('default')
    }
  }, [layoutManager, currentLayoutId, switchLayout])

  return {
    currentLayout,
    currentLayoutId,
    allLayouts: layoutManager.getAllLayouts(),
    switchLayout,
    updateLayout,
    addWidget,
    removeWidget,
    updateWidgetPosition,
    createLayout,
    deleteLayout
  }
}

export default DashboardLayoutManager
