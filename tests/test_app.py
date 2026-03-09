import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_200(self, client):
        """
        ARRANGE: Setup is handled by fixtures
        ACT: Make request to get all activities
        ASSERT: Verify response status and structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_activity_contains_required_fields(self, client):
        """
        ARRANGE: Setup is handled by fixtures
        ACT: Request activities and extract one
        ASSERT: Verify all required fields are present
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_activity_participants_are_list(self, client):
        """
        ARRANGE: Setup is handled by fixtures
        ACT: Request activities
        ASSERT: Verify participants field is a list
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_returns_200(self, client):
        """
        ARRANGE: Prepare a new email not yet registered
        ACT: Sign up the participant for an activity
        ASSERT: Verify successful response
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Prepare a new email and get initial participant count
        ACT: Sign up the participant
        ASSERT: Verify participant is added to activity list
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"]
        count_before = len(participants_before)
        
        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        assert len(participants_after) == count_before + 1
        assert email in participants_after
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Prepare non-existent activity name
        ACT: Attempt to sign up for non-existent activity
        ASSERT: Verify 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant_returns_400(self, client):
        """
        ARRANGE: Use an email already signed up for an activity
        ACT: Try to sign up the same participant again
        ASSERT: Verify 400 error
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_same_person_multiple_activities_allowed(self, client):
        """
        ARRANGE: Prepare a new participant and two different activities
        ACT: Sign up the same participant for two different activities
        ASSERT: Verify participant appears in both activities
        """
        # Arrange
        email = "multiactivity@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        client.post(f"/activities/{activity1}/signup?email={email}")
        client.post(f"/activities/{activity2}/signup?email={email}")
        
        # Assert
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant_returns_200(self, client):
        """
        ARRANGE: Use an email already signed up
        ACT: Unregister the participant
        ASSERT: Verify successful response
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant_from_activity(self, client):
        """
        ARRANGE: Get initial participant list and unregister count
        ACT: Unregister a participant
        ASSERT: Verify participant is removed from activity list
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"]
        count_before = len(participants_before)
        
        # Act
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        assert len(participants_after) == count_before - 1
        assert email not in participants_after
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        ARRANGE: Prepare non-existent activity name
        ACT: Attempt to unregister from non-existent activity
        ASSERT: Verify 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_non_participant_returns_400(self, client):
        """
        ARRANGE: Use an email not signed up for the activity
        ACT: Try to unregister a non-participant
        ASSERT: Verify 400 error
        """
        # Arrange
        email = "notstudent@mergington.edu"  # Not signed up
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_full_lifecycle_signup_unregister(self, client):
        """
        ARRANGE: Prepare test data
        ACT: Sign up, verify, then unregister
        ASSERT: Verify each state change
        """
        # Arrange
        email = "lifecycle@mergington.edu"
        activity = "Programming Class"
        
        # Act & Assert - Initial state
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Act & Assert - After signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Act & Assert - After unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_concurrent_participants_signup(self, client):
        """
        ARRANGE: Prepare multiple new participants
        ACT: Sign up multiple participants for same activity
        ASSERT: Verify all are added successfully
        """
        # Arrange
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        activity = "Gym Class"
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        response_after = client.get("/activities")
        participants = response_after.json()[activity]["participants"]
        assert len(participants) == count_before + len(emails)
        for email in emails:
            assert email in participants
