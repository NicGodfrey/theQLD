# 20-round legion — closed

Done with live agents: **R1–R20**. Sequential rule held: implement → test →
commit → one blocking verifier → fold → next. No remaining verifier slots.

| Agent | Model | Round | Slice | Status |
|---|---|---|---|---|
| fable-01 | claude-fable-5-thinking-high | 1 | fail-closed | done `bc-0aaa1b95-0380-54cf-bdfb-7be26a631fef` |
| opus-01 | claude-opus-5-thinking-high-fast | 2 | quote | done `bc-c218619b-4eeb-54b5-958e-9ce31c6b776c` |
| fable-02 | claude-fable-5-thinking-high | 3 | progress/SSE | done `bc-72e1141d-8dfb-5c2c-80a3-ccc9cfc130cd` |
| opus-02 | claude-opus-5-thinking-high-fast | 4 | download | done `bc-824042df-b2ae-521f-9de9-294a0d45e785` |
| fable-03 | claude-fable-5-thinking-high | 5 | upload | done `bc-1e3f17cc-b34e-5c43-95f0-bce5b0c4f942` |
| opus-03 | claude-opus-5-thinking-high-fast | 6 | camera | done `bc-d732bcab-e09d-5d4c-a2d4-6fac24eeecd2` |
| fable-04 | claude-fable-5-thinking-high | 7 | plan visible | done `bc-520ceeaa-f397-5a49-babb-1e07c2e60083` |
| opus-04 | claude-opus-5-thinking-high-fast | 8 | 4-up variants | done `bc-59bb5fa8-982e-506a-83b3-4ba25bb29d26` |
| fable-05 | claude-fable-5-thinking-high | 9 | undo | done `bc-8275a8f7-781f-5d18-bca1-feba9f3df131` |
| opus-05 | claude-opus-5-thinking-high-fast | 10 | brand kit | done `bc-a3da2941-bceb-5248-8900-c03ff9598864` |
| fable-06 | claude-fable-5-thinking-high | 11 | spot-edit | done `bc-218c832a-ac0d-5cf7-9b4e-f097beaead07` |
| opus-06 | claude-opus-5-thinking-high-fast | 12 | text layer | done `bc-8a0798e1-f1c8-5be7-acef-6143bc5bcfb1` |
| fable-07 | claude-fable-5-thinking-high | 13 | export zip | done `bc-4b7db339-3319-5f0b-9c98-d2194a4820a9` |
| opus-07 | claude-opus-5-thinking-high-fast | 14 | launcher | done `bc-a87b48b1-2bce-5790-9993-d4e777a16a1b` |
| fable-08 | claude-fable-5-thinking-high | 15 | host-pin | done `bc-0c059fa2-94ba-577f-911b-83b3d29efd47` |
| opus-08 | claude-opus-5-thinking-high-fast | 16 | budget 402 | done `bc-127658e9-1325-5838-be73-fee8d341a8ec` |
| fable-09 | claude-fable-5-thinking-high | 17 | CI | done `bc-8e733077-73e6-56a9-9e5f-eaacd80dcf12` |
| opus-09 | claude-opus-5-thinking-high-fast | 18 | live contract | done `bc-4f37d954-4a0b-5093-b44a-0e09cb824f7b` |
| fable-10 | claude-fable-5-thinking-high | 19 | eval fixtures | done `bc-0556ad0e-6b84-5fe6-b170-a36e89e0295f` |
| opus-10 | claude-opus-5-thinking-high-fast | 20 | scorecard | done `bc-30de5c2a-8e49-5f75-a7e6-7d97ef68c65a` |

Scorecard: technical 20/20, gate 16 met, `lovart_complete: false`,
`paid_loop_proven: false`. See `SCORECARD.json`.
