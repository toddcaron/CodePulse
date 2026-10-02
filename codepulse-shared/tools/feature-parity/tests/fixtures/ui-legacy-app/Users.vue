<template>
  <form @submit.prevent="save">
    <button @click="save">Save</button>
  </form>
  <router-link to="/users">Users</router-link>
</template>
<script setup>
const save = () => {};
</script>