module.exports = {
  outputDir: './dist/',
  devServer: {
    proxy: {
      '/token': {
        target: 'http://localhost:5000'
      },
      '/api': {
        target: 'http://localhost:5000'
      }
    }
  }
}
