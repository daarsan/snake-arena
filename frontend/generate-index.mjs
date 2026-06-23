import { writeFileSync } from 'node:fs'
import handler from './dist/server/server.js'

const response = await handler.fetch(new Request('http://localhost/'), {}, {})
const html = await response.text()
writeFileSync('dist/client/index.html', html)
console.log('Generated dist/client/index.html')
