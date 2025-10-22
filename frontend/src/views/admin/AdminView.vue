<template>
  <div class="min-h-screen bg-gray-100">
    <div class="flex">
      <!-- Sidebar -->
      <div class="w-64 bg-white shadow-sm min-h-screen">
        <div class="p-4 border-b">
          <h2 class="text-lg font-semibold">РђРґРјРёРЅ-РїР°РЅРµР»СЊ</h2>
        </div>
        <nav class="mt-4">
          <router-link 
            to="/admin/sessions" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            РЎРµСЃСЃРёРё
          </router-link>
          <router-link 
            to="/admin/users" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            РџРѕР»СЊР·РѕРІР°С‚РµР»Рё
          </router-link>
          <router-link 
            to="/admin/bonus-params" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            РџР°СЂР°РјРµС‚СЂС‹ РїСЂРµРјРёРё
          </router-link>
          <router-link 
            to="/admin/votes" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Р“РѕР»РѕСЃР°
          </router-link>
          <router-link 
            to="/admin/export" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Р­РєСЃРїРѕСЂС‚
          </router-link>
          <router-link 
            to="/admin/analytics" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            РђРЅР°Р»РёС‚РёРєР°
          </router-link>
        </nav>
      </div>
      
      <!-- Main content -->
      <div class="flex-1 p-8">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
// РђРґРјРёРЅСЃРєР°СЏ РїР°РЅРµР»СЊ Р±СѓРґРµС‚ СЂРµР°Р»РёР·РѕРІР°РЅР°
</script>
