

export const filesApi = {
  getTextFile: async (url: string) => {
    // We use a custom fetch here because api.get expects JSON response by default
    // and we need text/blob
    const response = await fetch(url)
    if (!response.ok) throw new Error('Failed to load text file')
    const blob = await response.blob()
    return await blob.text()
  }
}
