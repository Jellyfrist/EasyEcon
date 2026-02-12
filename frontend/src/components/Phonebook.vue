<template>
  <div class="container">
    <!-- Header -->
    <div id="header">
      <h1>{{ user ? `${user.name}'s Phonebook` : "Phonebook" }}</h1>
      <button v-if="user" @click="logout" class="logout-btn">Logout</button>
    </div>
    <div v-if="user">
      <!-- Add/Edit Form -->
      <div id="add-edit" v-show="showForm">
        <h2 id="add-edit-caption">Add/Edit a Contact:</h2>
        <form @submit.prevent="submitForm">
          <label for="firstname">ชื่อ</label>
          <input type="text" id="firstname" v-model="formData.firstname" placeholder="Your name.." required />
          <label for="lastname">นามสกุล</label>
          <input type="text" id="lastname" v-model="formData.lastname" placeholder="Your last name.." required />
          <label for="phone">โทรศัพท์</label>
          <input type="tel" id="phone" v-model="formData.phone" placeholder="Your phone number.." required />
          <input type="hidden" v-model="formData.id" />
          <div class="button-container">
            <input type="submit" value="Submit" />
            <button type="button" @click="clearForm">Clear</button>
            <button type="button" @click="toggleView">Cancel</button>
          </div>
        </form>
      </div>
      <!-- Contact Display -->
      <div id="contact_display" v-show="!showForm">
        <button @click="addContact" class="create-btn">Create Contact</button>
        <h2>Contacts:</h2>
        <table class="table-striped border-success" id="phonebook-table">
          <thead>
            <tr>
              <th>ชื่อ</th>
              <th>นามสกุล</th>
              <th>โทรศัพท์</th>
              <th>แก้ไข/ลบ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(contact, index) in contacts" :key="contact.id">
              <td>{{ contact.firstname }}</td>
              <td>{{ contact.lastname }}</td>
              <td>{{ contact.phone }}</td>
              <td>
                <a class="edit" @click="editContact(contact)">✏️</a>
                <a class="remove" @click="removeContact(contact.id)">🗑️</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "axios";
import { getUser, logout } from "@/services/auth"; // Import user state & logout function

export default {
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
      showForm: false,
      contacts: [],
      formData: { id: "", firstname: "", lastname: "", phone: "" },
      user: getUser(), // Get the logged-in user
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
        this.contacts = res.data;
      } catch (error) {
        console.error("Error fetching contacts:", error);
        this.response = `Error: ${error.message}`;
      }
    },
    async submitForm() {
      try {
        const url = this.formData.id ?
          `${this.apiBaseUrl}/lab10` :
          `${this.apiBaseUrl}/lab10`;
        console.log("Submitting form data with:", JSON.stringify(this.formData));

        const response = await axios.post(url, this.formData, {
          headers: { "Content-Type": "application/json" },
        });

        this.contacts = response.data;
        this.toggleView();
        this.clearForm();
      } catch (error) {
        console.error("Error submitting form:", error);
      }
    },
    clearForm() {
      this.formData = { id: "", firstname: "", lastname: "", phone: "" };
    },
    toggleView() {
      this.showForm = !this.showForm;
    },
    addContact() {
      this.clearForm();
      this.toggleView();
    },
    editContact(contact) {
      this.formData = { ...contact };
      this.toggleView();
    },
    async removeContact(id) {
      try {
        if (!confirm("Are you sure you want to delete this contact?")) return;
        const response = await axios.post(`${this.apiBaseUrl}/lab10/remove_contact`, { id }, {
          headers: { "Content-Type": "application/json" },
        });

        this.contacts = response.data;
      } catch (error) {
        console.error("Error removing contact:", error);
      }
    },
    logout() {
      logout(); // Call logout function from auth.js
      this.user = null; // Reset the UI state
    },
  },
  mounted() {
    this.fetchContacts();
  },
};
</script>
<style scoped>
@import "../assets/phonebook.css";

#header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  width: 100%;
}

.logout-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #218838;
}

.button-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

#phonebook-table>thead>tr>th {
  color: #28a745;
  font-weight: bold;
}

#add-edit>form>label {
  text-align: left;
  display: block;
}

#add-edit {
  margin-top: 20px;
}
</style>