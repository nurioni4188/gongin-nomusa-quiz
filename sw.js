/* RC35: cache shell on HTTPS and cache problem images only after viewing.
   Never fetch or publish content to any third-party endpoint. */
const CACHE_VERSION="nomusa-rc35-v1";
const SHELL=["./","./index.html","./data.js","./manifest.webmanifest","./icon.svg"];
self.addEventListener("install",e=>{
  e.waitUntil(caches.open(CACHE_VERSION).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith("nomusa-")&&k!==CACHE_VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  const url=new URL(e.request.url);
  if(url.origin!==self.location.origin||!url.pathname.startsWith(new URL(self.registration.scope).pathname))return;
  e.respondWith(caches.match(e.request).then(cached=>{
    if(cached)return cached;
    return fetch(e.request).then(res=>{
      if(res.ok && (url.pathname.includes("/img/")||SHELL.some(path=>url.pathname.endsWith(path.replace("./","/"))))){
        const copy=res.clone();caches.open(CACHE_VERSION).then(cache=>cache.put(e.request,copy)).catch(()=>{});
      }
      return res;
    });
  }));
});
