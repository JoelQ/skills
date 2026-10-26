#!/usr/bin/env python3
"""Generate synthetic Claude Code transcripts for testing defrag.

Each scenario is a list of steps. Step kinds:
  ("prompt", text, think_s)          human prompt after think_s seconds idle
  ("say", text, s)                   assistant text after s seconds
  ("tool", name, input, run_s, perm[, body, is_error])
                                     tool call; perm is None (auto-allowed),
                                     ("accept"|"reject", wait_s) for a human prompt
  ("ask", question, wait_s)          AskUserQuestion mid-run
  ("plan", wait_s)                   ExitPlanMode approval
  ("interrupt", after_s)             human interrupts the run
  ("cmd", name)                      local slash command
  ("compact", s)                     auto-compaction after s seconds (not a human stop)
  ("notify", text, s)                background task notification (not a human stop)
  ("apierror", text, s)              API error in place of a reply (e.g. an expired login)

Usage: synth.py OUT_DIR
"""
import json, os, sys, uuid
from datetime import datetime, timedelta, timezone


class Session:
    def __init__(self, start, cwd, branch='main'):
        self.t, self.cwd, self.id, self.rows, self.parent = start, cwd, str(uuid.uuid4()), [], None
        self.branch = branch

    def row(self, typ, message, **extra):
        u = str(uuid.uuid4())
        r = {'parentUuid': self.parent, 'isSidechain': False, 'type': typ, 'message': message, 'uuid': u,
             'timestamp': self.t.isoformat().replace('+00:00', 'Z'), 'cwd': self.cwd, 'sessionId': self.id,
             'permissionMode': 'default', 'version': '2.1.300', 'gitBranch': self.branch}
        r.update(extra)
        self.rows.append(r)
        self.parent = u

    def wait(self, s):
        self.t += timedelta(seconds=s)

    def run(self, steps):
        for st in steps:
            k = st[0]
            if k == 'prompt':
                self.wait(st[2])
                self.row('user', {'role': 'user', 'content': st[1]})
            elif k == 'cmd':
                self.row('user', {'role': 'user', 'content': '<command-name>%s</command-name>' % st[1]})
            elif k == 'say':
                self.wait(st[2])
                self.row('assistant', {'role': 'assistant', 'content': [{'type': 'text', 'text': st[1]}]})
            elif k in ('tool', 'ask', 'plan'):
                body, is_err = 'ok', False
                if k == 'tool':
                    name, inp, run_s, perm = st[1], st[2], st[3], st[4]
                    if len(st) > 5:
                        body, is_err = st[5], st[6]
                elif k == 'ask':
                    name, inp, run_s, perm = 'AskUserQuestion', {'questions': [{'question': st[1]}]}, 0, ('accept', st[2])
                else:
                    name, inp, run_s, perm = 'ExitPlanMode', {'plan': '...'}, 0, ('accept', st[1])
                tid = 'toolu_' + uuid.uuid4().hex[:20]
                self.wait(4)
                self.row('assistant', {'role': 'assistant', 'content': [{'type': 'tool_use', 'id': tid, 'name': name, 'input': inp}]})
                wait = run_s + (perm[1] if perm else 0)
                self.wait(wait)
                rejected = perm and perm[0] == 'reject'
                body = "The user doesn't want to proceed with this tool use." if rejected else body
                dec = ({'decision': perm[0], 'source': 'user'} if perm and k == 'tool'
                       else {'decision': 'accept', 'source': 'config', 'reasonType': 'rule'})
                self.row('user', {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': tid, 'content': body, 'is_error': bool(rejected or is_err)}]},
                         permissionDecision=dec)
            elif k == 'compact':
                self.wait(st[1])
                self.row('system', None, subtype='compact_boundary')
                self.row('user', {'role': 'user', 'content': 'This session is being continued from a previous conversation that ran out of context. Summary: ...'},
                         isCompactSummary=True)
            elif k == 'apierror':
                self.wait(st[2])
                self.row('assistant', {'role': 'assistant', 'content': [{'type': 'text', 'text': st[1]}]}, isApiErrorMessage=True)
            elif k == 'notify':
                self.wait(st[2])
                self.row('user', {'role': 'user', 'content': '<task-notification>%s</task-notification>' % st[1]})
            elif k == 'interrupt':
                self.wait(st[1])
                self.row('user', {'role': 'user', 'content': [{'type': 'text', 'text': '[Request interrupted by user]'}]})

    def save(self, d):
        p = os.path.join(d, self.id + '.jsonl')
        with open(p, 'w') as f:
            for r in self.rows:
                f.write(json.dumps(r) + '\n')
        return p


def bash(cmd, run=8, perm=None, body='ok', is_error=False):
    return ('tool', 'Bash', {'command': cmd}, run, perm, body, is_error)


def edit(path, run=1, perm=None):
    return ('tool', 'Edit', {'file_path': path}, run, perm)


def read(path):
    return ('tool', 'Read', {'file_path': path}, 1, None)


def work(n, files=('app/models/order.rb', 'app/services/sync.rb', 'spec/sync_spec.rb')):
    out = []
    for i in range(n):
        out += [read(files[i % len(files)]), edit(files[(i + 1) % len(files)], 1)]
    return out


def subagent(desc, run=300):
    return ('tool', 'Task', {'description': desc}, run, None)


T0 = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)

SCENARIOS = {
    # plan mode, then phase-by-phase execution, permission prompts on tests and git, commit chore at the end
    'phase-gated': [
        ('prompt', 'Add retry with backoff to the order sync job. Plan first.', 0),
        *work(3), ('plan', 140),
        ('say', 'Phase 1 done: extracted the HTTP client. Want me to continue with phase 2 (retry policy)?', 20),
        ('prompt', 'yes', 300),
        *work(4), bash('bin/rspec spec/sync_spec.rb', 40, ('accept', 90)), bash('bin/rspec spec/sync_spec.rb', 40, ('accept', 30)),
        ('say', 'Phase 2 done, tests pass. Shall I move on to phase 3 (dead-letter queue)?', 10),
        ('prompt', 'go ahead', 600),
        *work(6), bash('bin/rspec', 120, ('accept', 240)), bash('bin/rails db:migrate', 15, ('accept', 45)),
        ('say', 'All three phases complete. The full suite passes.', 10),
        ('prompt', 'commit this', 120),
        bash('git add -A', 1, ('accept', 20)), bash('git commit -m "Add retry to order sync"', 2, ('accept', 15)),
        ('say', 'Committed.', 3),
    ],
    # spec interview with many one-word answers, then one long build, then corrections
    'interview-long-tail': [
        ('prompt', 'I want an admin page to reconcile unmatched payments. Interview me before building.', 0),
        ('say', 'Should the page list only unmatched payments, or all payments with a filter? I recommend unmatched only.', 15),
        ('prompt', 'yes, unmatched only', 60),
        ('say', 'Should matching be manual (pick an invoice) or suggested? I recommend suggestions with manual confirm.', 10),
        ('prompt', 'yes', 45),
        ('say', 'Who can access it? I recommend finance admins only.', 10),
        ('prompt', 'yes', 30),
        ('say', 'Do you need an audit log of matches? I recommend yes.', 10),
        ('prompt', 'yes', 40),
        ('say', 'Should partial payments be matchable to multiple invoices?', 10),
        ('prompt', 'Yes. A payment can cover several invoices, and an invoice can be paid in several payments.', 120),
        ('say', 'Got it. I have enough to build. Shall I start?', 8),
        ('prompt', 'go', 200),
        *work(12, ('app/controllers/admin/reconciliations_controller.rb', 'app/views/admin/reconciliations/index.html.erb', 'app/models/payment_match.rb', 'spec/requests/reconciliations_spec.rb')),
        bash('bin/rspec spec/requests', 60, ('accept', 400)),
        ('say', 'The reconciliation page is built and the request specs pass.', 10),
        ('prompt', "The suggestions ignore the remittance email reference, which is the main signal. That's the whole point.", 1500),
        *work(4), bash('bin/rspec spec/requests', 60, ('accept', 30)),
        ('say', 'Suggestions now rank by remittance reference first.', 5),
        ('prompt', "Partial matches don't show the remaining balance.", 900),
        *work(2),
        ('say', 'Remaining balance now shows on partial matches.', 5),
        ('prompt', 'Run the full suite, it should be green', 600),
        bash('bin/rspec', 180, ('accept', 60)),
        ('say', 'Two failures in unrelated specs, both pre-existing on main.', 5),
        ('prompt', 'ok commit and open a PR', 300),
        bash('git add -A', 1, ('accept', 30)), bash('git commit -m "Payment reconciliation page"', 2, ('accept', 10)),
        bash('gh pr create --fill', 5, ('accept', 20)),
        ('say', 'PR opened.', 3),
    ],
    # well-specified ask, long autonomous run with an allowlist, short tail
    'clean-run': [
        ('cmd', '/model'),
        ('prompt', 'Implement the CSV export described in docs/export-spec.md. Tests in spec/exports. Commit when green.', 0),
        *work(6, ('app/services/csv_export.rb', 'spec/exports/csv_export_spec.rb', 'docs/export-spec.md')),
        ('apierror', 'API Error: 403 The security token included in the request is expired. Please run /login', 5),
        ('cmd', '/login'),
        ('prompt', 'continue', 1500),
        *work(9, ('app/services/csv_export.rb', 'spec/exports/csv_export_spec.rb', 'docs/export-spec.md')),
        bash('bin/rspec spec/exports', 30), bash('bin/rspec', 150), bash('git commit -am "CSV export"', 2),
        ('say', 'CSV export implemented per the spec, the suite is green, and it is committed.', 10),
        ('prompt', 'Nice. Also add the totals row mentioned at the end of the spec.', 400),
        *work(3), bash('bin/rspec spec/exports', 30), bash('git commit -am "Totals row"', 2),
        ('say', 'Added the totals row and committed.', 5),
    ],
    # mid-run clarifying question, an interrupt and a rejected command
    'drift': [
        ('prompt', 'Speed up the invoices index page; it times out for big accounts.', 0),
        *work(3), ('ask', 'Is it OK to add a database index on invoices.account_id, created_at?', 500),
        *work(4), bash('bin/rails db:migrate', 15, ('accept', 20)),
        bash('bin/rails runner "Invoice.reindex_all"', 0, ('reject', 60)),
        ('say', 'I added the index. Next I was going to backfill a cached total column.', 10),
        ('prompt', "Don't add a cached column, just paginate. I don't want schema churn for this.", 240),
        *work(2), ('interrupt', 30),
        ('prompt', 'Use the existing Pagy setup, not Kaminari', 20),
        *work(4), bash('bin/rspec spec/requests/invoices_spec.rb', 40, ('accept', 35)),
        ('say', 'The index page now paginates with Pagy and loads in under 300ms on the large fixture.', 5),
    ],
    # long autonomous hill-climb on a branch, stalled overnight by an expired login
    'hill-climb': [
        ('prompt', 'Hill-climb the flaky spec list in tmp/flaky.txt. Fix one at a time, commit each fix, keep going until the list is empty.', 0),
        *[x for i in range(6) for x in (subagent('investigate flaky spec %d' % i, 900), *work(2), ('notify', 'background rspec --repeat 20 finished: 0 failures', 400),
                                        bash('git commit -am "Fix flaky spec %d"' % i, 2), *([('compact', 30)] if i in (2, 4) else []))],
        bash('snow sql -q "select * from ci_runs limit 100"', 3, None,
             'Error: Authentication token has expired. The user must authenticate again (SSO login required).', True),
        ('say', 'Fixed 6 of 9 flaky specs. The remaining 3 need CI history from Snowflake, but my session token expired. Please log in and tell me to continue.', 10),
        ('prompt', 'logged in, continue', 8 * 3600),
        *[x for i in range(6, 9) for x in (subagent('investigate flaky spec %d' % i, 900), *work(2), bash('git commit -am "Fix flaky spec %d"' % i, 2))],
        ('say', 'All 9 flaky specs fixed, one commit each.', 10),
    ],
    # UI bug the agent can't see: the human is the eyes, pasting what the browser shows
    'ping-pong': [
        ('prompt', 'The invoice PDF preview modal is blank in Safari. Fix it.', 0),
        *work(3),
        ('say', 'The iframe src was missing a content type. Fixed, it should render now.', 10),
        ('prompt', 'Still blank. Console says: Refused to display in a frame because it set X-Frame-Options to deny', 180),
        *work(2),
        ('say', 'Set X-Frame-Options to sameorigin for the preview route. Try again?', 5),
        ('prompt', 'Now it shows but the modal is cut off at the bottom', 150),
        *work(2),
        ('say', 'Adjusted the modal max-height. How does it look?', 5),
        ('prompt', 'Better, but scrolling inside the PDF scrolls the page behind it', 200),
        *work(2),
        ('say', 'Added overscroll containment on the modal. Can you check?', 5),
        ('prompt', 'Works in Safari now. Check Chrome too', 120),
        ('say', 'I cannot open a browser here. Could you check Chrome?', 5),
        ('prompt', 'Chrome is fine. Commit it', 240),
        bash('git commit -am "Fix PDF preview modal"', 2, None),
        ('say', 'Committed.', 3),
    ],
    # the payments page again, after the fixes: batched interview, then one closed loop
    'payments-closed-loop': [
        ('prompt', 'Build an admin page to reconcile unmatched payments. Ask anything you need in one batch with your defaults, then build. '
                   'Verify with request specs and a screenshot, commit and open a draft PR when green.', 0),
        *work(2),
        ('say', 'Questions, with my defaults: (1) unmatched only? yes (2) suggest matches with manual confirm? yes (3) finance admins only? yes '
                '(4) audit log? yes (5) can one payment cover several invoices? I assume no. (6) What signal matters most for matching?', 15),
        ('prompt', 'Defaults are fine except 5: many-to-many, both ways. 6: the remittance email reference is the main signal.', 180),
        *work(12, ('app/controllers/admin/reconciliations_controller.rb', 'app/views/admin/reconciliations/index.html.erb', 'app/models/payment_match.rb', 'spec/requests/reconciliations_spec.rb')),
        bash('bin/rspec spec/requests', 60), bash('node script/screenshot.js /admin/reconciliations', 20),
        *work(3, ('app/views/admin/reconciliations/index.html.erb',)), bash('bin/rspec', 180),
        bash('git add -A', 1), bash('git commit -m "Payment reconciliation page"', 2), bash('gh pr create --draft --fill', 5),
        ('say', 'Built, verified with request specs and a screenshot, and opened a draft PR.', 5),
    ],
    # review-and-polish session on the hill-climb branch: recurring rework themes
    'polish': [
        ('prompt', 'Review the commits on this branch with me. First: fix 3 adds a RetryHelper class used once. Inline it.', 0),
        *work(2),
        ('say', 'Inlined the helper.', 5),
        ('prompt', 'Remove the comments that just restate the code, throughout the branch.', 300),
        *work(5),
        ('say', 'Removed redundant comments in 7 files.', 5),
        ('prompt', "Fix 6 stubs Time.now globally; we use travel_to in this codebase. Same for fix 8.", 420),
        *work(3),
        ('say', 'Switched both to travel_to.', 5),
        ('prompt', 'Rename wait_for_it to wait_until_idle, and squash into logical commits', 360),
        *work(3), bash('git rebase -i main', 30, None),
        ('say', 'Renamed and squashed into 4 commits.', 5),
    ],
}

if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else 'synthetic'
    os.makedirs(d, exist_ok=True)
    branches = {'hill-climb': 'fix/flaky-specs', 'polish': 'fix/flaky-specs', 'ping-pong': 'fix/pdf-preview'}
    for i, (name, steps) in enumerate(SCENARIOS.items()):
        s = Session(T0 + timedelta(days=i), '/work/billing-app', branches.get(name, 'main'))
        s.run(steps)
        s.rows.append({'type': 'ai-title', 'aiTitle': name, 'sessionId': s.id})
        print(s.save(d))
