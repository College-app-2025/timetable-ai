import React, { useState } from 'react';
import { Clock, User, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { VoteProposal } from '../types';
import { formatDistanceToNow } from 'date-fns';

interface VoteCardProps {
  proposal: VoteProposal;
  onVote: (proposalId: string, vote: boolean) => void;
  hasVoted?: boolean;
  userVote?: boolean;
  disabled?: boolean;
}

const VoteCard: React.FC<VoteCardProps> = ({
  proposal,
  onVote,
  hasVoted = false,
  userVote,
  disabled = false
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleVote = async (vote: boolean) => {
    if (disabled || hasVoted || isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await onVote(proposal.id, vote);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'border-blue-200 bg-blue-50';
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'expired':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-gray-200 bg-white';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <AlertCircle size={16} className="text-blue-600" />;
      case 'completed':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'expired':
        return <XCircle size={16} className="text-gray-600" />;
      default:
        return <AlertCircle size={16} className="text-gray-600" />;
    }
  };

  const getVotePercentage = (votes: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((votes / total) * 100);
  };

  const isExpired = new Date(proposal.deadline) < new Date();
  const canVote = proposal.status === 'active' && !hasVoted && !isExpired && !disabled;

  return (
    <div className={`card transition-all duration-200 ${getStatusColor(proposal.status)}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {getStatusIcon(proposal.status)}
              <span className="text-sm font-medium text-gray-700 capitalize">
                {proposal.status}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 text-lg leading-tight">
              {proposal.title}
            </h3>
          </div>
        </div>

        {/* Description */}
        <div className="text-gray-600 text-sm leading-relaxed">
          {proposal.description}
        </div>

        {/* Class Details */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="text-sm text-gray-700">
            <div className="font-medium mb-1">Class Details:</div>
            <div>{proposal.class_details}</div>
          </div>
        </div>

        {/* Teacher Information */}
        <div className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="text-sm">
              <div className="text-gray-500">Original Teacher</div>
              <div className="font-medium text-gray-900">{proposal.original_teacher}</div>
            </div>
            <div className="text-gray-400">→</div>
            <div className="text-sm">
              <div className="text-gray-500">Substitute Teacher</div>
              <div className="font-medium text-gray-900">{proposal.substitute_teacher}</div>
            </div>
          </div>
        </div>

        {/* Voting Results */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Voting Results</span>
            <span className="text-xs text-gray-500">
              {proposal.votes.total} total votes
            </span>
          </div>
          
          <div className="space-y-2">
            {/* Yes votes */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span className="text-sm text-gray-700">Yes</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-900">
                  {proposal.votes.yes}
                </span>
                <span className="text-xs text-gray-500">
                  ({getVotePercentage(proposal.votes.yes, proposal.votes.total)}%)
                </span>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getVotePercentage(proposal.votes.yes, proposal.votes.total)}%` }}
              />
            </div>
            
            {/* No votes */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <XCircle size={16} className="text-red-600" />
                <span className="text-sm text-gray-700">No</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-900">
                  {proposal.votes.no}
                </span>
                <span className="text-xs text-gray-500">
                  ({getVotePercentage(proposal.votes.no, proposal.votes.total)}%)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Deadline */}
        <div className="flex items-center text-sm text-gray-600">
          <Clock size={16} className="mr-2" />
          <span>
            {isExpired ? 'Voting expired' : 'Voting ends'} {' '}
            {formatDistanceToNow(new Date(proposal.deadline), { addSuffix: true })}
          </span>
        </div>

        {/* User Vote Status */}
        {hasVoted && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <CheckCircle size={16} className="text-blue-600" />
              <span className="text-sm text-blue-800">
                You voted: <span className="font-medium">{userVote ? 'Yes' : 'No'}</span>
              </span>
            </div>
          </div>
        )}

        {/* Voting Buttons */}
        {canVote && (
          <div className="flex space-x-3">
            <button
              onClick={() => handleVote(true)}
              disabled={isSubmitting}
              className="flex-1 btn-primary bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Submitting...' : 'Vote Yes'}
            </button>
            <button
              onClick={() => handleVote(false)}
              disabled={isSubmitting}
              className="flex-1 btn-secondary border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Submitting...' : 'Vote No'}
            </button>
          </div>
        )}

        {/* Disabled state */}
        {!canVote && !hasVoted && (
          <div className="text-center py-3">
            <span className="text-sm text-gray-500">
              {isExpired ? 'Voting has ended' : 'Voting is not available'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

interface VoteGridProps {
  proposals: VoteProposal[];
  onVote: (proposalId: string, vote: boolean) => void;
  userVotes?: Record<string, boolean>;
  loading?: boolean;
}

const VoteGrid: React.FC<VoteGridProps> = ({
  proposals,
  onVote,
  userVotes = {},
  loading = false
}) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, index) => (
          <div key={index} className="card animate-pulse">
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
              <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              <div className="h-20 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (proposals.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <AlertCircle size={48} className="mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No voting proposals</h3>
        <p className="text-gray-600">There are currently no class change proposals to vote on.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {proposals.map((proposal) => (
        <VoteCard
          key={proposal.id}
          proposal={proposal}
          onVote={onVote}
          hasVoted={userVotes.hasOwnProperty(proposal.id)}
          userVote={userVotes[proposal.id]}
        />
      ))}
    </div>
  );
};

export { VoteCard, VoteGrid };
export default VoteCard;
