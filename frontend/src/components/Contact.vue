<template>
  <div class="container">
    <h1>{{ user ? `${user.name}'s ` : "" }}Contact List (Raw Response)</h1>
    <pre>{{ response }}</pre>
  </div>
</template>
<script>
import axios from "axios";
import { getUser } from "@/services/auth"; //  Import getUser()

export default {
  name: "Contact",
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL, //  Use API base URL
      response: null,
      user: getUser(), //  Fetch logged-in user
    };
  },
  methods: {
    async fetchContacts() {
      try {
        console.log("Fetching contacts from API...");

        //  Make API request (Axios sends JWT automatically via cookies)
        const res = await axios.get(`${this.apiBaseUrl}/lab10/contacts`);

        console.log("API Response Object:", res);

        if (!res.data) {
          throw new Error("No data received from API");
        }

        console.log("Parsed Data:", res.data);
        this.response = JSON.stringify(res.data, null, 2);
      } catch (error) {
        console.error("Error fetching contacts:", error);
        this.response = `Error: ${error.message}`;
      }
    }
  },
  mounted() {
    this.fetchContacts(); //  Fetch contacts on mount
  }
};
</script>
<style scoped>
.container {
  margin-top: 20px;
}

h1 {
  margin-bottom: 20px;
}

pre {
  text-align: left;
  background: #f8f9fa;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  white-space: pre-wrap;
  /* Wrap long lines */
  word-break: break-word;
  /* Break words if necessary */
  font-family: "Courier New", Courier, monospace;
  /* Monospaced font for JSON display */
  font-size: 18px;
  /* Optional: Adjust font size for better readability */
  line-height: 1.5;
  /* Optional: Adjust line height for better readability */
}
</style>