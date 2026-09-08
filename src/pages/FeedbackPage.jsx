import React, { useState } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import { Star, Send, CheckCircle2, MessageSquare } from 'lucide-react';
import './FeedbackPage.css';

export function FeedbackPage() {
  const [rating, setRating] = useState(5);
  const [category, setCategory] = useState('AI Chatbot Accuracy');
  const [comments, setComments] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [feedbackList, setFeedbackList] = useState([
    {
      id: 1,
      category: 'AI Chatbot Accuracy',
      rating: 5,
      comment: 'Excellent retrieval of TDS limits for IS 10500 drinking water specs.',
      date: 'Today, 03:10 PM'
    },
    {
      id: 2,
      category: 'Producer Verification',
      rating: 4,
      comment: 'CML licence search instantly loaded factory location.',
      date: 'Yesterday'
    }
  ]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!comments.trim()) {
      setErrorMessage('Please enter your feedback comments before submitting.');
      return;
    }

    setErrorMessage('');
    const newEntry = {
      id: Date.now(),
      category,
      rating,
      comment: comments,
      date: 'Just now'
    };

    setFeedbackList([newEntry, ...feedbackList]);
    setSubmitted(true);
    setComments('');
    setTimeout(() => setSubmitted(false), 4000);
  };

  return (
    <div className="feedback-page">
      <PageHeader
        title="Feedback & User Support"
        description="Share your experience or report suggestions to help us improve the BIS AI Assistant."
        breadcrumbs={['Portal', 'Feedback']}
        badge={<Badge variant="neutral">User Support</Badge>}
      />

      <DisclaimerBanner />

      <div className="feedback-grid">
        <Card title="Submit Portal Feedback" subtitle="Your input directly improves our guardrailed AI RAG model and UI portal.">
          {submitted && (
            <div className="alert-success-banner mb-4">
              <CheckCircle2 size={20} />
              <span>Thank you! Your feedback has been logged successfully.</span>
            </div>
          )}

          {errorMessage && (
            <div className="alert-error-banner mb-4">
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group mb-4">
              <label className="form-label">Feedback Category:</label>
              <select className="form-select" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="AI Chatbot Accuracy">AI Chatbot Accuracy</option>
                <option value="Standards Search & Filters">Standards Search & Filters</option>
                <option value="Producer Verification">Producer Verification</option>
                <option value="HUID Hallmark Checker">HUID Hallmark Checker</option>
                <option value="UI & Responsiveness">UI & Responsiveness</option>
              </select>
            </div>

            <div className="form-group mb-4">
              <label className="form-label">Rating (1 to 5 Stars):</label>
              <div className="stars-row">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    className={`star-btn ${rating >= star ? 'active' : ''}`}
                    onClick={() => setRating(star)}
                  >
                    <Star size={24} fill={rating >= star ? '#f59e0b' : 'none'} color={rating >= star ? '#f59e0b' : '#cbd5e1'} />
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group mb-4">
              <label className="form-label">Detailed Feedback & Comments:</label>
              <textarea
                rows={4}
                className="form-textarea"
                placeholder="Share your thoughts or report any issues..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
              />
            </div>

            <Button type="submit" variant="primary" icon={Send}>
              Submit Feedback
            </Button>
          </form>
        </Card>

        {/* Recent Feedback Summary */}
        <Card title="Recent Feedback Entries" subtitle="Community & Admin feedback history">
          <div className="feedback-entries-list">
            {feedbackList.map((fb) => (
              <div key={fb.id} className="entry-card mb-3">
                <div className="entry-header mb-1">
                  <span className="entry-cat">{fb.category}</span>
                  <div className="entry-stars">
                    {Array.from({ length: fb.rating }).map((_, i) => (
                      <Star key={i} size={14} fill="#f59e0b" color="#f59e0b" />
                    ))}
                  </div>
                </div>
                <p className="entry-comment">{fb.comment}</p>
                <span className="entry-date text-muted text-xs">{fb.date}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

export default FeedbackPage;
