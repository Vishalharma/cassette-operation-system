with tab4:

    st.subheader("👥 User Management Panel")

    if st.session_state.role != "admin":
        st.warning("Only admin can access user management.")
    else:

        # ======================
        # CREATE USER
        # ======================
        st.markdown("### ➕ Create New User")

        with st.form("create_user"):

            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "user"])

            create = st.form_submit_button("Create User")

            if create:
                if new_username.strip() == "" or new_password.strip() == "":
                    st.error("Username and Password required")
                else:
                    add_user(new_username, new_password, new_role)
                    st.success(f"User '{new_username}' created successfully")

        # ======================
        # VIEW USERS
        # ======================

        st.markdown("### 📋 Existing Users")

        users_df = get_users()
        st.dataframe(users_df, use_container_width=True)

        # ======================
        # DELETE USER
        # ======================

        st.markdown("### 🗑 Delete User")

        if len(users_df) > 0:

            del_user = st.selectbox(
                "Select User",
                users_df["username"].tolist()
            )

            if del_user == "admin":
                st.warning("Admin cannot be deleted")
            else:
                if st.button("Delete User"):
                    delete_user(del_user)
                    st.success(f"User '{del_user}' deleted")
                    st.rerun()
